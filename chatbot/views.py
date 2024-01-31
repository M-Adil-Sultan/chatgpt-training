import os
import pandas as pd
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Chat
from train.models import Train_dataset
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
# from langchain.document_loaders import PandasDataFrameLoader
from langchain_community.document_loaders import DataFrameLoader
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = "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"

def initialize_chain():
    # Get the data from the database
    queryset = Train_dataset.objects.all()
    qa_data = queryset.values('question', 'answers')
    # print("qa_data:", qa_data)
    
    # Convert the data into a DataFrame
    df = pd.DataFrame.from_records(qa_data)
    # print("df:", df)

    if os.path.exists("mydata/SocialLabsTrainingFormat.xlsx"):
        os.remove("mydata/SocialLabsTrainingFormat.xlsx")
    
    # Save the DataFrame as an Excel file
    directory_path = "mydata/"
    excel_file_path = os.path.join(directory_path, "SocialLabsTrainingFormat.xlsx")

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Save the Excel file
    df.to_excel(excel_file_path, index=False)

    # Load documents from the Pandas DataFrame using PandasDataFrameLoader
    # loader = DataFrameLoader(df, page_content_column="answers")
    loader = DirectoryLoader(directory_path)
    documents = loader.load()

    # Access the content and metadata of each document
    # for document in documents:
    #     content = document.page_content
    #     metadata = document.metadata

    # Initialize the text splitter and embeddings
    text_splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()

    # # Create the Chroma vector store
    docsearch = Chroma.from_documents(texts, embeddings)

    # Create the RetrievalQA object
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever())

    # Create the ConversationalRetrievalChain
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-4"),
        retriever=docsearch.as_retriever(search_kwargs={"k": 1}),
    )

    return chain

# Initialize the chain outside the view function
chain = initialize_chain()

def chain_initializer(request):
    global chain
    chain = initialize_chain()
    return redirect('chatbot')

def chat_with_langchain(query, chat_history):
    result = chain({"question": query, "chat_history": chat_history})
    answer = result['answer']
    chat_history.append((query, answer))
    return answer, chat_history

def ask_openai(message):
    # Implement your OpenAI logic here
    # For now, using the chat_with_langchain function
    global chain
    chat_history = []  # Initialize chat history
    answer, chat_history = chat_with_langchain(message, chat_history)
    return answer

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        db_response = Train_dataset.objects.filter(question__iexact=message).first()
        if db_response is not None and db_response.answers is not None:
            return JsonResponse({'message': message, 'response': db_response.answers})

        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot.html', {'chats': chats})

# Remaining views (login, register, logout, chatlog) remain unchanged.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def chatlog(request):
    chats = Chat.objects.filter(user=request.user)
    return render(request, 'chatbot_log.html', {'chats': chats})

def insert_to_train(request, chat_id):
    # Get the chat entry
    chat = get_object_or_404(Chat, id=chat_id)

    # Insert into Train_dataset
    Train_dataset.objects.create(question=chat.message, answers=chat.response)

    return HttpResponse("Inserted into Train_dataset successfully!")

def modify_log(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        message = request.POST.get('message')
        response = request.POST.get('response')
        print(f"Received form data - chat_id: {chat_id}, message: {message}, response: {response}")
        # update data to database
        chat = Chat.objects.get(id=chat_id)
        chat.message = message
        chat.response = response
        chat.save()

        return redirect("chatlog")
    else:
        return HttpResponse("Invalid request")