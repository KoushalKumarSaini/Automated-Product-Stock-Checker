# Start with an official AWS Lambda base image for Python 3.9.
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container.
WORKDIR /var/task

# Copy the requirements file and install the dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your application's code into the working directory.
COPY . .

# Set the command for the container. This line is changed to match your file name.
# It now looks for 'handler' in the 'check_stock.py' file.
CMD [ "check_stock.handler" ]
