import pandas as pd
import os
from django.shortcuts import render, redirect
from .models import Train_dataset
from .forms import TrainForm
from django.core.files.storage import FileSystemStorage

def train(request):
    # Fetch all data from the Train_dataset model
    question_answers = Train_dataset.objects.all()

    # Handle form submission
    if request.method == 'POST':
        form = TrainForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the form data to the Train_dataset model
            form.save()

            # Handle uploaded Excel file
            excel_file = request.FILES.get('excel_file')
            if excel_file:
                handle_uploaded_excel(excel_file)

            return redirect('train')  # Redirect to the same page after submission
    else:
        form = TrainForm()

    return render(request, 'train.html', {'question_answers': question_answers, 'form': form})

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
