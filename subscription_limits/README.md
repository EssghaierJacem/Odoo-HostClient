# Subscription Limits Manager for Odoo 17

A comprehensive Odoo module that allows you to manage subscription limits for sales orders and invoices with a beautiful, modern interface and real-time notifications.

## 🚀 Features

### Core Functionality

- **Dynamic Subscription Plans**: Create and manage subscription plans with customizable limits
- **User Subscription Management**: Assign plans to users and track their usage
- **Real-time Limit Enforcement**: Automatically prevent users from exceeding their limits
- **Usage Tracking**: Monitor sales orders and invoices usage in real-time
- **Automatic Notifications**: Built-in notification system with Odoo's bus system

### Beautiful UI/UX

- **Modern Dashboard**: Interactive dashboard with usage statistics and progress bars
- **Kanban Views**: Visual management of subscription plans and users
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Smooth Animations**: Engaging user experience with CSS animations
- **Color-coded Status**: Easy-to-understand status indicators

### Advanced Features

- **Multiple Duration Types**: Monthly, quarterly, yearly, and unlimited plans
- **Flexible Pricing**: Set different prices for each plan
- **Usage Analytics**: Detailed usage reports and statistics
- **Cron Jobs**: Automatic subscription expiration handling
- **API Endpoints**: RESTful API for external integrations

## 📋 Requirements

- Odoo 17.0 or later
- Python 3.8+
- PostgreSQL 12+
- Modern web browser with JavaScript enabled

## 🛠️ Installation

1. **Download the Module**

   ```bash
   cd /path/to/odoo/custom_addons
   git clone <repository-url> subscription_limits
   ```

2. **Install Dependencies**

   ```bash
   pip install -r subscription_limits/requirements.txt
   ```

3. **Update Odoo Configuration**
   Add the custom_addons path to your Odoo configuration file:

   ```ini
   [options]
   addons_path = /path/to/odoo/addons,/path/to/odoo/custom_addons
   ```

4. **Install the Module**
   - Start/restart Odoo server
   - Go to Apps menu in Odoo
   - Search for "Subscription Limits Manager"
   - Click Install

## 🎯 Quick Start Guide

### 1. Create Subscription Plans

1. Navigate to **Subscription Limits > Management > Subscription Plans**
2. Click **Create** to add a new plan
3. Configure:
   - **Plan Name**: e.g., "Basic Plan"
   - **Plan Code**: e.g., "BASIC"
   - **Max Sales Orders**: e.g., 10
   - **Max Invoices**: e.g., 10
   - **Price**: e.g., $29.00
   - **Duration Type**: Monthly/Quarterly/Yearly/Unlimited
   - **Features**: List of included features

### 2. Assign Plans to Users

1. Go to **Subscription Limits > Management > User Subscriptions**
2. Click **Create** to assign a plan to a user
3. Select:
   - **User**: Choose the user
   - **Plan**: Select the subscription plan
   - **Start Date**: Set the subscription start date
4. Click **Activate** to activate the subscription

### 3. Monitor Usage

1. Access the **Dashboard** from the main menu
2. View real-time usage statistics
3. Monitor progress bars for sales orders and invoices
4. Check remaining limits

## 🔧 Configuration

### Default Plans

The module comes with 4 pre-configured plans:

- **Basic Plan**: 10 sales orders, 10 invoices - $29/month
- **Professional Plan**: 50 sales orders, 50 invoices - $79/month
- **Enterprise Plan**: 200 sales orders, 200 invoices - $199/month
- **Unlimited Plan**: Unlimited usage - $499/month

### Customization

You can customize:

- Plan limits and pricing
- Duration types
- Features and descriptions
- Colors and icons
- Notification settings

## 📊 Usage Examples

### Creating a Sales Order

```python
# The module automatically checks limits before creating sales orders
sale_order = self.env['sale.order'].create({
    'partner_id': partner.id,
    'user_id': user.id,
    # ... other fields
})

# If user has reached their limit, an error will be raised
# with a notification sent to the user
```

### Checking User Limits

```python
# Get current subscription limits
limits = user.get_subscription_limits()
print(f"Sales Orders: {limits['sales_orders_used']}/{limits['max_sales_orders']}")
print(f"Invoices: {limits['invoices_used']}/{limits['max_invoices']}")

# Check if user can create sales orders
if user.can_create_sales_order():
    # Proceed with creation
    pass
else:
    # Handle limit reached
    pass
```

### Sending Notifications

```python
# Send a warning notification
self.env['bus.bus']._sendone(
    user.partner_id,
    'simple_notification',
    {
        'type': 'warning',
        'title': 'Usage Warning',
        'message': f'You have {remaining} sales orders remaining.'
    }
)
```

## 🎨 UI Components

### Dashboard

- **Usage Statistics**: Visual representation of current usage
- **Progress Bars**: Animated progress bars showing usage percentage
- **Quick Actions**: Buttons for common tasks
- **Status Indicators**: Color-coded subscription status

### Kanban Views

- **Plan Cards**: Visual representation of subscription plans
- **User Cards**: User subscription status and usage
- **Drag & Drop**: Easy management of subscriptions

### Notifications

- **Real-time Alerts**: Instant notifications for limit warnings
- **Action Buttons**: Quick actions from notifications
- **Auto-dismiss**: Configurable auto-close timing

## 🔌 API Endpoints

### Get Usage Data

```javascript
// Get current user's usage data
rpc
  .query({
    route: "/subscription/api/usage",
  })
  .then(function (data) {
    console.log(data);
  });
```

### Get Available Plans

```javascript
// Get all available subscription plans
rpc
  .query({
    route: "/subscription/api/plans",
  })
  .then(function (data) {
    console.log(data.plans);
  });
```

### Upgrade Subscription

```javascript
// Upgrade to a new plan
rpc
  .query({
    route: "/subscription/api/upgrade",
    params: { plan_id: planId },
  })
  .then(function (result) {
    console.log(result);
  });
```

## 🚨 Notifications

The module sends notifications in the following scenarios:

### Warning Notifications

- When user has ≤3 sales orders remaining
- When user has ≤3 invoices remaining
- When subscription is about to expire

### Error Notifications

- When user tries to exceed their limits
- When subscription has expired
- When subscription is suspended

### Success Notifications

- When subscription is activated
- When subscription is renewed
- When limits are reset

## 🔄 Cron Jobs

### Automatic Tasks

- **Check Expired Subscriptions**: Runs daily to expire outdated subscriptions
- **Send Reminder Notifications**: Automated reminder system
- **Usage Statistics Update**: Regular usage data updates

## 🛡️ Security

### Access Control

- **User Permissions**: Users can only see their own subscriptions
- **Manager Access**: Sales managers can view all subscriptions
- **Admin Access**: System administrators have full access

### Data Protection

- **Audit Trail**: Complete history of subscription changes
- **Data Validation**: Input validation and constraint checking
- **Secure API**: Protected API endpoints with user authentication

## 🧪 Testing

### Demo Data

The module includes comprehensive demo data:

- Sample users with different subscription plans
- Example sales orders and invoices
- Various subscription states for testing

### Test Scenarios

1. **Limit Enforcement**: Test that users cannot exceed their limits
2. **Notification System**: Verify notifications are sent correctly
3. **Plan Upgrades**: Test subscription plan changes
4. **Expiration Handling**: Test automatic expiration

## 📈 Performance

### Optimization Features

- **Database Indexing**: Optimized database queries
- **Caching**: Smart caching of usage data
- **Lazy Loading**: Efficient loading of large datasets
- **Background Processing**: Non-blocking operations

### Monitoring

- **Usage Metrics**: Track module performance
- **Error Logging**: Comprehensive error tracking
- **Performance Alerts**: Monitor system performance

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This module is licensed under LGPL-3.0.

## 🆘 Support

### Documentation

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [API Reference](docs/api_reference.md)

### Community

- [GitHub Issues](https://github.com/your-repo/issues)
- [Odoo Forum](https://www.odoo.com/forum/help-1)
- [Discord Channel](https://discord.gg/your-channel)

### Professional Support

For professional support and customizations, contact:

- Email: support@yourcompany.com
- Phone: +1-555-0123
- Website: https://yourcompany.com

## 🔄 Changelog

### Version 17.0.1.0.0

- Initial release
- Basic subscription management
- Real-time notifications
- Beautiful dashboard
- API endpoints

### Planned Features

- Advanced analytics
- Payment integration
- Multi-currency support
- Mobile app
- White-label options

---

**Made with ❤️ for the Odoo community**
