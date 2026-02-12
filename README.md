
# Intelligent Email Classifier Using DistilBERT

The Intelligent Email Classifier project leverages the power of DistilBERT, a state-of-the-art natural language processing (NLP) model, to automatically categorize emails. This project aims to improve email management efficiency by accurately classifying incoming emails into predefined categories such as Sales, HR, Development.

Furthermore, the emails are subcategorized into different priorities as well as escalation and non-escalation categories, ensuring a more nuanced and efficient email management system.

The labeling informaiton can be found here in [label.txt](https://github.com/Spacecode10/EmailClass/blob/main/dataset/labels.txt)







## Workflow

We implemented Google authentication to securely fetch all emails from a user's Gmail account. After fetching the emails, we classify them accordingly and display the categorized emails in a user-friendly interface within the Django app.

We utilize a Redis database for caching each user's emails. All fetched emails are stored in Redis, allowing the Django app to efficiently retrieve and display the cached emails.

In the Django app, we use three different models for email classification: 

1)For Department and Subtypes.

2)For prioritizing emails.

3)For classifing escalation mails.

Here is the diagram showing Workflow

![dfd]()






## Tech Stack

**Client:** Html, CSS, JavaScript

**Server:** Django, Redis

**API:** Gmail API


## Run Locally


Clone the project

```bash
  git clone https://github.com/Spacecode10/EmailClass
```

Go to the project directory

```bash
  cd EmailClass/EmailClassifier
```

Install dependencies

```bash
  pip install -r requirements.txt
```
Install the redis server for windows from the below link
https://github.com/tporadowski/redis/releases

Start the server

```bash
  python manage.py runserver
```

