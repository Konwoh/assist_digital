from pydantic_ai import ModelMessage, UsageLimits, ModelRequest, UserPromptPart, Agent
from pydantic import BaseModel
from backend.agents.agents_schema import RAGAnswer, ConfidenceEvaluation


class ChatAnswer(BaseModel):
    rag_agent_response: RAGAnswer
    confidence_agent_response: ConfidenceEvaluation

class ChatService:
    def __init__(self, rag_agent, rewrite_agent, confidence_agent: Agent[object, ConfidenceEvaluation], max_history_messages: int = 20):
        self.rag_agent = rag_agent
        self.rewrite_agent = rewrite_agent
        self.confidence_agent = confidence_agent
        self.max_history_messages = max_history_messages
        self.conversation_history: list[ModelMessage] = []    
        
    def _is_tool_response_message(self, message: ModelMessage) -> bool:
        parts = getattr(message, "parts", [])
        tool_response_parts = {"ToolReturnPart", "RetryPromptPart"}
        return bool(parts) and all(
            part.__class__.__name__ in tool_response_parts
            for part in parts
        )

    def _trim_conversation_history(self, messages: list[ModelMessage]) -> list[ModelMessage]:
        trimmed_messages = messages[-self.max_history_messages:]

        while trimmed_messages and self._is_tool_response_message(trimmed_messages[0]):
            trimmed_messages = trimmed_messages[1:]

        return trimmed_messages
        
    
    def _evaluate_confidence(
        self,
        user_query: str,
        improved_query: str,
        entity_focus: list[str],
        rag_answer: RAGAnswer,
        rag_messages: list[ModelMessage],
    ) -> ConfidenceEvaluation:
        confidence_prompt = f"""
        original user prompt: {user_query}

        improved user prompt: {improved_query}

        entity focus: {entity_focus}

        rag answer:
        {rag_answer.response}

        rag sources:
        {rag_answer.sources}

        rag messages and retrieved context:
        {rag_messages}
        """

        confidence_result = self.confidence_agent.run_sync(
            confidence_prompt,
            usage_limits=UsageLimits(request_limit=3),
        )

        return confidence_result.output
    
    def add_feedback_to_history(self, feedback: bool) -> None:
        feedback_text = (
            "Feedback zum vorherigen Assistant-Output: Der User hat die letzte Antwort mit Daumen hoch bewertet. "
            "Behalte den Antwortstil und die Herangehensweise bei, falls es zur naechsten Frage passt."
            if feedback
            else
            "Feedback zum vorherigen Assistant-Output: Der User hat die letzte Antwort mit Daumen runter bewertet. "
            "Passe die naechste Antwort entsprechend an: pruefe die Quellen genauer, antworte praeziser und vermeide denselben Fehler."
        )

        self.conversation_history.append(
            ModelRequest(
                parts=[UserPromptPart(content=feedback_text)],
                metadata={
                    "type": "feedback",
                    "rating": "good" if feedback else "bad",
                },
            )
        )
        self.conversation_history = self._trim_conversation_history(self.conversation_history)
    
    def answer_question(self, user_query: str) -> ChatAnswer:
        rewrite_result = self.rewrite_agent.run_sync(
            user_query,
            usage_limits=UsageLimits(request_limit=1),
        )

        improved_query = rewrite_result.output.search_query

        prompt = f"""
        original user prompt: {user_query}
        
        improved user prompt: {improved_query}
        
        entity focus: {rewrite_result.output.entity_focus}
        """
        
        
        result = self.rag_agent.run_sync(
            prompt,
            message_history=self.conversation_history,
        )
        rag_answer = result.output

        confidence = self._evaluate_confidence(
            user_query=user_query,
            improved_query=improved_query,
            entity_focus=rewrite_result.output.entity_focus,
            rag_answer=rag_answer,
            rag_messages=result.all_messages(),
        )

        if confidence.label == "mittel":
            retry_prompt = f"""
                Die vorherige Antwort wurde vom Validator nur mit 'mittel' bewertet.

                Originale Nutzerfrage:
                {user_query}

                Verbesserte Suchfrage:
                {improved_query}

                Vorherige Antwort:
                {rag_answer.response}

                Validator-Begründung:
                {confidence.explanation}

                Fehlende Belege:
                {confidence.missing_evidence}

                Aufgabe:
                Prüfe die Frage erneut mit retrieval_tool.
                Verbessere die Antwort nur, wenn du bessere Belege findest.
                Wenn die fehlenden Informationen nicht belegbar sind, sage das ehrlich.
                Nutze kein internes Wissen.
            """

            result = self.rag_agent.run_sync(
                retry_prompt,
                message_history=self.conversation_history,
            )

            rag_answer = result.output
            confidence = self._evaluate_confidence(
                user_query=user_query,
                improved_query=improved_query,
                entity_focus=rewrite_result.output.entity_focus,
                rag_answer=rag_answer,
                rag_messages=result.all_messages(),
            )

        self.conversation_history = self._trim_conversation_history(result.all_messages())
        response = ChatAnswer(rag_agent_response=rag_answer, confidence_agent_response=confidence)

        return response
