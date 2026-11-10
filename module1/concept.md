There are a few concepts to understand:

1. LangGraph:
   - Python and Javascript Library
   - Allows creation of agent workflows
2. LangGraph API:
   - Bundles the graph code
   - Provides a tsks queue for managing asynchronous operations
   - Offers persistence for maintaining state across interactions
3. LangGraph Cloud:
   - LangGraph API can be hosted via LangGraph Cloud (Hosted service)
   - Allows deployment of graphs from GitHub repositories
   - This provides monitoring, tracing, and API documentations for deployed graphs
   - Accessible via a unique URL for each deployment
4. LangGraph Studio
   - IDE for LangGraph applications
   - Uses the API as its back-end, allowing real-time testing and exploration of graphs
   - Can be run locally or with cloud-deployment
5. LangGraph SDK
   - Python library for programmatically interacting with LangGraph graphs
   - Provides a consistent interface for working with graphs, whether served locally or in the cloud
   - We can connect to them via our cloud URL or our URL supplied by LangGraph Studio
   - Allows creation of clients, access to assistants, thread management, and execution of runs
