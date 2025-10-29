How to start Miranda4

Make sure you’re in the project root:

cd C:\Users\eman7\OneDrive\Desktop\Dev_Bois\Miranda4


Activate the venv (CMD):

.\.venv\Scripts\activate


Your prompt will now show (.venv) — cool. Don’t type that part.

Run Uvicorn (from the root):

uvicorn backend.app:app --reload