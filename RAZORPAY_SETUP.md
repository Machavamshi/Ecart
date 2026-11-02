# Razorpay Payment Integration Setup Guide

This guide will help you integrate Razorpay payment gateway into your e-commerce platform.

## Prerequisites

- Python 3.7+
- Flask application running
- MySQL database
- Razorpay account (free to create at https://razorpay.com)

## Step 1: Install Razorpay SDK

The Razorpay Python SDK is already added to `requirements.txt`. Install it using:

```bash
pip install -r requirements.txt
```

Or directly:

```bash
pip install razorpay
```

## Step 2: Get Your Razorpay API Keys

1. Visit [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up or log in with your account
3. Navigate to **Settings → API Keys**
4. You'll see two keys:
   - **Key ID** (public key)
   - **Key Secret** (private key - keep this secret!)

## Step 3: Configure API Keys

### Option A: Using Environment Variables (Recommended)

1. Create a `.env` file in your project root (based on `.env.example`):

```bash
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxx
```

2. The application will automatically read these environment variables

### Option B: Direct Configuration (Not Recommended for Production)

Edit `app.py` and locate the Razorpay configuration section:

```python
# Around line 30 in app.py
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"
```

## Step 4: Integration Overview

### Files Modified/Created:

1. **requirements.txt** - Added `razorpay` package
2. **app.py** - Added payment routes:
   - `/user/checkout` - Checkout page
   - `/user/verify-payment` - Payment verification
   - `/user/payment-success/<order_id>` - Success page
   - `/user/payment-failed` - Failed page

3. **database/payment_utility.py** - New module containing:
   - `create_razorpay_order()` - Create payment order
   - `create_order_in_db()` - Save order to database
   - `clear_user_cart()` - Clear cart after success
   - `verify_payment()` - Verify payment signature
   - `get_cart_items_for_checkout()` - Get cart items
   - `get_cart_total_amount()` - Calculate total

4. **Templates Created**:
   - `templates/user/checkout.html` - Checkout page
   - `templates/user/payment.html` - Razorpay payment form
   - `templates/user/payment_success.html` - Success confirmation
   - `templates/user/payment_failed.html` - Failure page

## Step 5: Database Schema

The `ORDERS` table already has payment-related fields:

```sql
PAYMENT_METHOD ENUM('COD','UPI','CARD','NETBANKING','RAZORPAY')
PAYMENT_STATUS ENUM('PENDING','SUCCESS','FAILED')
```

Orders created via Razorpay will have:
- `PAYMENT_METHOD = 'RAZORPAY'`
- `PAYMENT_STATUS = 'SUCCESS'` (after verification)

## Step 6: Payment Flow

```
User Cart → Checkout Page → Razorpay Payment Page → 
  → Payment Verification → Order Creation → 
  → Cart Cleared → Success Page
```

### User Journey:

1. User clicks "Proceed to Checkout" from cart
2. Checkout page displays order summary
3. User clicks "Pay Now with Razorpay"
4. Razorpay payment gateway opens
5. User completes payment
6. System verifies payment signature
7. Order is created in database
8. Cart is cleared
9. Success page is shown with order ID

## Step 7: Testing

### Test Mode (Development)

Razorpay provides test credentials and test cards:

**Test Credit Card:**
- Card Number: `4111 1111 1111 1111`
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3-4 digits (e.g., 123)

**Amount:**
- Any amount in test mode will work
- Use 0 or small amounts for testing

### To Enable Test Mode:

1. In your Razorpay Dashboard, toggle the **Test Mode** switch (usually at the top)
2. Use test API keys (they start with `rzp_test_`)

### Testing Locally:

```python
# Test payment creation
python -c "
from database.payment_utility import create_razorpay_order
order = create_razorpay_order(500, 'Test Order')
print(order)
"
```

## Step 8: Webhook Integration (Optional but Recommended)

For production, implement webhooks for payment confirmations:

1. Go to **Settings → Webhooks** in Razorpay dashboard
2. Add webhook URL: `https://yourdomain.com/webhook/razorpay`
3. Subscribe to events:
   - `payment.authorized`
   - `payment.failed`
   - `order.paid`

## Step 9: Security Considerations

### Important Security Notes:

1. **Never commit `.env` file** - Add to `.gitignore`:
   ```
   .env
   *.pem
   ```

2. **Keep Key Secret confidential** - Never expose in client-side code

3. **Always verify signatures** - Implemented in `verify_payment()` function

4. **Use HTTPS in production** - Razorpay requires secure connections

5. **Validate all user inputs** - Already implemented in routes

## Step 10: Error Handling

The system handles various error scenarios:

- **Invalid payment signature** → Redirect to failure page
- **Database insert failure** → Rollback and show error
- **Missing cart items** → Redirect to cart with warning
- **API connection failure** → Show user-friendly error message

## Troubleshooting

### Issue: "Invalid API Key"

**Solution:** 
- Verify you've added `razorpay` to requirements.txt
- Check your Key ID and Key Secret are correct
- Use test keys (rzp_test_*) for development

### Issue: "Payment signature mismatch"

**Solution:**
- Ensure `RAZORPAY_KEY_SECRET` is correct
- Check for extra whitespace in environment variables
- Verify customer payment data matches server record

### Issue: "Order not created in database"

**Solution:**
- Check database connection
- Verify ORDERS table exists and has correct schema
- Check for MySQL errors in console output
- Ensure USER_ID and PRODUCT_ID foreign keys are valid

### Issue: Cart items not cleared after order

**Solution:**
- Verify USER_ID is correctly passed
- Check CART table has correct USER_ID values
- Ensure database transaction completes successfully

## Production Deployment

### Pre-deployment Checklist:

- [ ] Switch to live API keys (rzp_live_*)
- [ ] Enable HTTPS/SSL
- [ ] Set up environment variables on server
- [ ] Test complete payment flow with real card
- [ ] Configure error logging and monitoring
- [ ] Set up email notifications for orders
- [ ] Test database backup and recovery
- [ ] Configure webhook endpoints
- [ ] Enable 2FA on Razorpay account
- [ ] Review security policies

### Deployment Steps:

1. Copy `.env` to server (keep secret)
2. Install dependencies: `pip install -r requirements.txt`
3. Run database migration if needed
4. Restart Flask application
5. Test payment with small amount
6. Monitor logs for errors

## Support

For issues with:
- **Razorpay integration**: Visit [Razorpay Docs](https://razorpay.com/docs/)
- **This implementation**: Check code comments and logs
- **Account issues**: Contact [Razorpay Support](https://razorpay.com/contact-us/)

## Resources

- [Razorpay Python SDK](https://github.com/razorpay/razorpay-python)
- [Razorpay API Documentation](https://razorpay.com/docs/api/)
- [Checkout.js Documentation](https://razorpay.com/docs/razorpay-js/)
- [Payment Gateway Concepts](https://razorpay.com/docs/payments/)

---

**Last Updated:** February 21, 2026

For the latest updates and documentation, visit https://razorpay.com/docs/
