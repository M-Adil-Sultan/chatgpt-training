import os
import pandas as pd
from .forms import TrainForm
from .models import Train_dataset
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def train(request):
    
    # Fetch all data from the Train_dataset model
    all_question_answers = Train_dataset.objects.all()
    request.session['success'] = request.session.get('success',0) + 3

    # Paginate the queryset
    paginator = Paginator(all_question_answers, 20)
    page = request.GET.get('page')
    try:
        question_answers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        question_answers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        question_answers = paginator.page(paginator.num_pages)

    # Handle form submission
    if request.method == 'POST':
        form = TrainForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("Form is valid")  # Print for debugging
            # Save the form data to the Train_dataset model
            form.save()

            # Handle uploaded Excel file
            excel_file = request.FILES.get('excel_file')
            print("Excel File:", excel_file)  # Print the uploaded Excel file for debugging
            if excel_file:
                print("Excel File is valid")  # Print for debugging
                handle_uploaded_excel(excel_file)
            else:
                print("Excel File is not valid")  # Print for debugging
            request.session['success'] = 2
            return redirect('train')  # Redirect to the same page after submission
    else:
        form = TrainForm()
    return render(request, 'train.html', {'question_answers': question_answers, 'form': form})
    


def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            handle_uploaded_excel(excel_file)
            return redirect('train')
        else:
            return HttpResponse("No file provided.")

    return HttpResponse("Invalid request.")


def handle_uploaded_excel(excel_file):
    # Save the uploaded Excel file to a temporary location
    fs = FileSystemStorage()
    filename = fs.save(excel_file.name, excel_file)
    file_path = os.path.join(fs.location, filename)  # Obtain the absolute file system path

    print("File Path:", file_path)  # Print the file path for debugging

    # Check if the file exists
    if os.path.exists(file_path):
        # Read data from the Excel file into a Pandas DataFrame
        df = pd.read_excel(file_path)

        # Save the DataFrame data to the Train_dataset model
        Train_dataset.objects.bulk_create(
            [Train_dataset(question=row['Questions'], answers=row['Answers']) for index, row in df.iterrows()]
        )

        # Delete the temporary file after processing
        fs.delete(filename)
    else:
        print("File does not exist:", file_path)


def delete(request, id):
    question_answers = Train_dataset.objects.get(id=id)
    question_answers.delete()
    return redirect('train')
