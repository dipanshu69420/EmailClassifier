from django.shortcuts import render, redirect
from .models import Email
from .fetch_email import fetch_email, get_cached_emails, TOKEN_FILE
from .classifier import predict_class
from django.contrib.auth import logout as auth_logout
import os
import redis
import pickle
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseServerError


r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def email_details(request, subject):
    print(subject)
    try:
        classified_emails_data = r.get('emails')
        if classified_emails_data:
            classified_emails = pickle.loads(classified_emails_data)
            print("Retrieved classified emails from cache:", classified_emails)
            selected_email = [email for email in classified_emails if email['subject'] == subject]
            if selected_email:
                email_details = selected_email[0]
            else:
                return HttpResponseServerError("Email not found with the given subject.")
        else:
            print("No data found in cache.")
            email_details = None
    except Exception as e:
        print("Error retrieving classified emails from cache:", e)
        return HttpResponseServerError("Error retrieving classified emails from cache.")

    return render(request, 'email_details.html', {'email_details': email_details})

def user_logout(request):
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    r.delete('emails')
    auth_logout(request)
    return redirect('index')

def index(request):
    error_message = None
    classified_emails = []

    try:
        emails = get_cached_emails()
        print("Fetched cached emails:", emails)

        if not emails:
            print("No cached emails found, fetching from Gmail.")
            emails = fetch_email()
            print("Fetched emails from Gmail:", emails)

        model_path = r"D:\EmailClassify\EmailClassifier\model-params"
        tokenizer_path = r"D:\EmailClassify\EmailClassifier\model-params"
        classifier = predict_class(model_path, tokenizer_path)

        for email in emails:
            print("Processing email:", email)
            if 'predicted_class' not in email or email['predicted_class'] is None:
                classification = classifier.classify(email['body'])
                email['predicted_class'] = classification

            if 'priority' not in email or email['priority'] is None:
                priority = classifier.prioritize(email['body'])
                if priority == 'High Priority':
                    priority = 'High'
                elif priority == 'Medium Priority':
                    priority = 'Medium'
                else :
                    priority = 'Low'

                email['priority'] = priority

            if 'escalation' not in email or email['escalation'] is None:
                escalation = classifier.escalation(email['body'])
                email['escalation'] = escalation

            email_objs = Email.objects.filter(subject=email['subject'], From=email['from'])
            if email_objs.exists():
                email_obj = email_objs.first()
                email_obj.predicted_class = email['predicted_class']
                email_obj.priority = email['priority']
                email_obj.escalation=email['escalation']
                email_obj.save()
            else:
                email_obj = Email.objects.create(
                    From=email['from'],
                    To=email['to'],
                    subject=email['subject'],
                    body=email['body'],
                    predicted_class=email['predicted_class'],
                    priority=email['priority'],
                    escalation=email['escalation']
                )

            classified_emails.append({
                'from': email['from'],
                'to': email['to'],
                'subject': email['subject'],
                'body': email['body'],
                'classification': email['predicted_class'],
                'priority': email['priority'],
                'decoded_mail': email.get('decoded_mail'),
                'escalation': email['escalation']
            })
            print("Appended classified email:", classified_emails[-1])
        classified_emails.sort(key=lambda x: {'High': 0, 'Medium': 1, 'Low': 2}.get(x.get('priority', 'Low'), 2),reverse=False)
        print("Updating cache with classified emails.")

        if 'subject' in request.GET:
            subject = request.GET['subject']
            return redirect(reverse('email-details', kwargs={'subject': subject}))
        try:
            r.set('emails', pickle.dumps(classified_emails))
            print("Cache updated with classified emails.")
        except Exception as e:
            error_message = f"An error occurred while updating cache: {e}"
            print("Error updating cache:", error_message)


        print("Cache updated with classified emails.")
    except Exception as e:
        error_message = f"An error occurred while fetching emails: {e}"
        print("Error:", error_message)

    return render(request, 'classify.html', {'classified_emails': classified_emails, 'error_message': error_message})