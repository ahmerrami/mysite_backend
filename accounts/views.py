# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
import requests
import json

User = get_user_model()

def password_reset_request(request):
    """
    Vue pour demander la réinitialisation du mot de passe
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                
                # Générer un token de réinitialisation Django natif
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Construire l'URL de réinitialisation
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Contenu de l'email
                subject = f'[{settings.SOCIETE}] Réinitialisation de votre mot de passe'
                message = f"""
Bonjour,

Vous avez demandé la réinitialisation de votre mot de passe pour votre compte {settings.SOCIETE}.

Cliquez sur le lien suivant pour créer un nouveau mot de passe :
{reset_url}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.

Cordialement,
L'équipe {settings.SOCIETE}
                """.strip()
                
                # Envoyer l'email
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, 'Un email de réinitialisation a été envoyé à votre adresse.')
                    return redirect('password_reset_sent')
                except Exception as e:
                    print(f"ERROR sending email: {str(e)}")
                    messages.error(request, f'Erreur lors de l\'envoi de l\'email: {str(e)}')
                    
            except User.DoesNotExist:
                # Pour des raisons de sécurité, on affiche le même message
                messages.success(request, 'Si cette adresse email existe, un email de réinitialisation a été envoyé.')
                return redirect('password_reset_sent')
            except Exception as e:
                messages.error(request, f'Erreur système: {str(e)}')
                print(f"DEBUG: Exception: {str(e)}")
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'envoi: {str(e)}')
        else:
            messages.error(request, 'Veuillez saisir une adresse email.')
    
    return render(request, 'accounts/password_reset_form.html')

def password_reset_sent(request):
    """
    Page de confirmation d'envoi de l'email de reset
    """
    return render(request, 'accounts/password_reset_sent.html')

def password_reset_confirm(request, uidb64, token):
    """
    Vue pour confirmer la réinitialisation avec le token Django natif
    """
    try:
        # Décoder l'UID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password and password == password_confirm:
                # Réinitialiser le mot de passe
                user.set_password(password)
                user.save()
                
                messages.success(request, 'Votre mot de passe a été réinitialisé avec succès.')
                return redirect('admin:login')
            else:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
        
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': True,
            'form_url': request.get_full_path()
        })
    else:
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': False
        })

def password_reset_complete(request):
    """
    Page de confirmation de réinitialisation réussie
    """
    return render(request, 'accounts/password_reset_complete.html')
