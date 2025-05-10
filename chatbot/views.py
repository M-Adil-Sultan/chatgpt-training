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
from langchain.chains import ConversationalRetrievalChain, RetrievalQA, StuffDocumentsChain, LLMChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import uuid
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = "sk-sBlTgTX3mOMp0ycR5m15T3BlbkFJ4hlErtP5VWu"

# Define a new prompt template for combining documents
new_combining_prompt = ChatPromptTemplate(
    input_variables=['context', 'question'],
    messages=[
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=['context'],
                template="Based on the following context, provide a friendly and helpful response to the question. If you’re unsure, it’s okay to say that you don’t know. Here’s the context:\n{context}"
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=['question'],
                template="What do you need help with?\n{question}"
            )
        )
    ]
)

# Update the StuffDocumentsChain with the new prompt
combining_chain = StuffDocumentsChain(
    llm_chain=LLMChain(
        prompt=new_combining_prompt,
        llm=ChatOpenAI(model="gpt-4")
    ),
    document_variable_name='context'
)

# Define a new prompt template for the question generator
new_question_generator_prompt = PromptTemplate(
    input_variables=['chat_history', 'question'],
    template="Based on this conversation and the follow-up question, rephrase the question in a way that sounds natural and friendly:\n\nChat History:\n{chat_history}\nFollow-Up Input: {question}\nRephrased Question:"
)

# Update the QuestionGenerator chain with the new prompt
question_generator_chain = LLMChain(
    prompt=new_question_generator_prompt,
    llm=ChatOpenAI(model="gpt-4")
)

def initialize_chain():
    # Get the data from the database
    queryset = Train_dataset.objects.all()
    qa_data = queryset.values('question', 'answers')
    
    # Convert the data into a DataFrame
    df = pd.DataFrame.from_records(qa_data)

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
    loader = DirectoryLoader(directory_path)
    documents = loader.load()

    # Initialize the text splitter and embeddings
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()

    # Create the Chroma vector store
    docsearch = Chroma.from_documents(texts, embeddings)

    # Create the ConversationalRetrievalChain with updated components
    retriever = VectorStoreRetriever(
        vectorstore=docsearch,
        search_kwargs={"k": 1}
    )

    chain = ConversationalRetrievalChain(
        combine_docs_chain=combining_chain,
        question_generator=question_generator_chain,
        retriever=retriever
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
            chat = Chat(user=request.user, message=message, response=db_response.answers, created_at=timezone.now())
            chat.save()
            print(f"I came from db {db_response.answers} :--------------------------------")
            return JsonResponse({'message': message, 'response': db_response.answers})

        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        print(f"----------------I came from Openai  {response}")
        return JsonResponse({'message': message, 'response': response})
    dict = {}
    for chat in chats:
        dict[uuid.uuid4().hex[:6].upper()] = chat
    return render(request, 'chatbot.html', {'chats': dict.items()})

#------------------------------------------------------------------
# Remaining views (login, register, logout, chatlog) remain unchanged.
#------------------------------------------------------------------


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
    
def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.is_active = False  # Set user as inactive until admin approval
                user.save()
                

                # Send email to admin for approval
                email_from = settings.EMAIL_HOST_USER
                base_url = settings.BASE_URL
                recipient_list = ['info@nativebrains.com', 'danish.nisar@nativebrains.com'] # add recipient email here
                # Load email template
                html_message = render_to_string('request_approval_email_new.html', {'user_id':user.id,'username': username, 'email': email,'base_url': base_url,})
                plain_message = strip_tags(html_message)
                
                # To enable sending email uncomment
                # send_mail(
                #     'New User Registration - Approval Required',
                #     plain_message,
                #     email_from,
                #     recipient_list,
                #     html_message=html_message,
                #     fail_silently=False,
                # )
                
                # Redirect user to the "Wait for Approval" page
                return render(request, 'wait_for_approval.html')
                

            except Exception as e:
                print(f"Error Creating account: {e}")
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')



def approve_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    # Activate the user account
        user.is_active = True
        user.save()
        email_from = settings.EMAIL_HOST_USER
        base_url = settings.BASE_URL
        recipient_list = [user.email, ] # add recipient email here
        # Load email template
        html_message = render_to_string('approval_email.html', {'username': user.username, 'email': user.email,'base_url': base_url,})
        plain_message = strip_tags(html_message)
        
        # send_mail(
        #     'THE SOCIAL SALES LAB - Registeration Approved',
        #     plain_message,
        #     email_from,
        #     recipient_list,
        #     html_message=html_message,
        #     fail_silently=False,
        # )
        # Redirect to a success page or any other appropriate page
        return render(request, 'success.html', {'user_approved': "True"}) 
    except User.DoesNotExist:
        return None
    
    

def logout(request):
    auth.logout(request)
    return redirect('login')

def chatlog(request):
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
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
        # print(f"Received form data - chat_id: {chat_id}, message: {message}, response: {response}")
        # update data to database
        chat = Chat.objects.get(id=chat_id)
        chat.message = message
        chat.response = response
        chat.save()

        return redirect("chatlog")
    else:
        return HttpResponse("Invalid request")