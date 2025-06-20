# # reminder_agent.py

# from langchain.agents import initialize_agent, Tool
# from langchain.chat_models import ChatOpenAI
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Pinecone

# # 1️⃣ Fetch tasks due within 24 h
# def fetch_due_tasks(_input: str):
#     from pymongo import MongoClient
#     client = MongoClient("mongodb://…")
#     db = client.mydb
#     now = datetime.utcnow()
#     tomorrow = now + timedelta(hours=24)
#     tasks = list(db.tasks.find({
#         "deadline": {"$gte": now, "$lt": tomorrow},
#         "reminderSent": False
#     }))
#     return tasks  # a list of dicts

# # 2️⃣ Send email (or dashboard push)
# def send_reminder_email(payload: dict):
#     # payload example: {"to": "...", "subject": "...", "body": "..."}
#     import sendgrid
#     sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_KEY"))
#     mail = Mail(
#       from_email="no-reply@yourapp.com",
#       to_emails=payload["to"],
#       subject=payload["subject"],
#       html_content=payload["body"]
#     )
#     sg.send(mail)
#     return "Email sent"

# # 3️⃣ RAG‑driven personalization
# def personalize_message(task: dict):
#     # Load your vector store of past reminders
#     embeddings = OpenAIEmbeddings()
#     store = Pinecone.from_existing_index("user-history", embeddings)
#     docs = store.similarity_search(f"user:{task['user_id']}", k=3)
    
#     # Craft a prompt with history + task
#     prompt = f"""
#     You are a reminder assistant. Based on these past notes:
#     {docs}
#     Write a friendly reminder for this task:
#     Title: {task['title']}
#     Due: {task['deadline']}
#     """
#     llm = ChatOpenAI(temperature=0.7)
#     response = llm.predict(prompt)
#     return response
