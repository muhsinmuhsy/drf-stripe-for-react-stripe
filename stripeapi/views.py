import logging
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class CreateSubscription(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        email = request.data.get('email')
        payment_method_id = request.data.get('payment_method_id')
        price_id = request.data.get('price_id')
        logger.info(f'User ID: {user_id}, Payment Method ID: {payment_method_id}, Price ID: {price_id}')
        
        try:
            # Retrieve or create the CustomUser
            custom_user, created = CustomUser.objects.get_or_create(
                user_id=user_id,
                defaults={'email': email}
            )

            # Update email if the user already exists and the email is different
            if not created and custom_user.email != email:
                custom_user.email = email
                custom_user.save()

                # Update email in Stripe if the customer exists
                if custom_user.stripe_customer_id:
                    stripe.Customer.modify(
                        custom_user.stripe_customer_id,
                        email=email
                    )

            # Create or retrieve Stripe customer
            if created or not custom_user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=custom_user.email,
                    payment_method=payment_method_id,
                    invoice_settings={'default_payment_method': payment_method_id}
                )
                custom_user.stripe_customer_id = customer.id
                custom_user.save()
            else:
                customer = stripe.Customer.retrieve(custom_user.stripe_customer_id)

            # Create Stripe subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                expand=['latest_invoice.payment_intent']
            )

            # Save the subscription in the database
            sub = Subscription(
                custom_user=custom_user,
                stripe_subscription_id=subscription.id
            )
            sub.save()

            return Response(subscription, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Stripe error: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class StripeWebhook(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Add this to your settings.py

        event = None

        try:
            # Verify the webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            logger.error(f'Invalid payload: {str(e)}')
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(f'Invalid signature: {str(e)}')
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            # Handle successful payment here
            logger.info(f'Payment succeeded for invoice: {invoice}')

        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            # Handle subscription creation here
            logger.info(f'Subscription created: {subscription}')

        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            # Handle subscription update here
            logger.info(f'Subscription updated: {subscription}')

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            # Handle subscription cancellation here
            logger.info(f'Subscription canceled: {subscription}')

        else:
            logger.info(f'Unhandled event type: {event["type"]}')

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
