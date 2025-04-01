from typing import Annotated, Any

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langgraph.graph import StateGraph, state
from pinecone import Pinecone, ServerlessSpec  # type: ignore[import-untyped]
from pydantic import Field

from app.core.agents import BaseAgent, BaseState
from app.core.agents.registry import register_agent
from app.core.utils import reduce_docs


class RetrievalState(BaseState):
    """State object for the Retrieval Agent workflow."""

    question: str
    documents: Annotated[list[Document], reduce_docs] = Field(default_factory=list)


class RetrievalAgent(BaseAgent):
    """
    Retrieval Agent that finds and returns relevant documents from the knowledge base.
    """

    name: str = "retrieval"
    description: str = "Retrieves relevant documents from the knowledge base"
    system_prompt: str = ""

    def __init__(
        self,
        *,
        thread_id: str,
        model_name: str,
    ) -> None:
        super().__init__(thread_id=thread_id, model_name=model_name)
        self.vector_store = self._init_vector_store()
        self.retriever = MultiQueryRetriever.from_llm(
            retriever=self.vector_store.as_retriever(),
            llm=self.model,
        )
        self._graph = self._create_graph()

    def _init_vector_store(self) -> PineconeVectorStore:
        embedding = OpenAIEmbeddings(model="text-embedding-3-large")
        dimension = embedding.embed_query(".")

        pc = Pinecone()
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if self.thread_id not in existing_indexes:
            pc.create_index(
                name=self.thread_id,
                dimension=dimension,
                metric="cosine",
                timeout=30,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        index = pc.Index(name=self.thread_id)
        vector_store = PineconeVectorStore(index=index, embedding=embedding)
        return vector_store

    async def add_documents(self, documents: list[Document]) -> None:
        await self.vector_store.aadd_documents(documents)

    def _create_graph(self) -> state.CompiledStateGraph:
        async def retrieve_documents(state: RetrievalState) -> dict[str, Any]:
            docs = await self.retriever.ainvoke(state.question)
            message = AIMessage(
                content=f"Retrieving {len(docs)} documents relevant to the query."
            )
            return {"documents": docs, "messages": [message]}

        # Build workflow graph
        workflow = StateGraph(RetrievalState)
        workflow.add_node("retrieve", retrieve_documents)

        workflow.add_edge("__start__", "retrieve")
        workflow.add_edge("retrieve", "__end__")

        graph = workflow.compile(self.memory)
        graph.name = "Retrieval Agent"
        return graph


# Register the agent
register_agent(RetrievalAgent.name, RetrievalAgent)
