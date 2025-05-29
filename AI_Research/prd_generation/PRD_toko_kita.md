# PRODUCT REQUIREMENTS DOCUMENT (PRD)

## E-Commerce Application "Toko Kita"

### Introduction

This Product Requirements Document (PRD) is based on
Business Requirements Document (BRD) for the development of "Toko Kita" e-commerce application. This PRD aims to
provide technical guidance and details regarding the features to be developed in the
application.

### Product Description

"Toko Kita" is an e-commerce platform that connects local MSME sellers with
buyers. This application provides various features to facilitate online transactions in a safe, easy, and efficient
manner.

### Product Objective

- Increase sales of local MSME products
- Expand market reach for sellers
- Provide an easy and safe online shopping experience for buyers
- Increase company revenue through sales commissions

### Target User

**1. Sellers:**

- Local MSMEs
- Small and medium entrepreneurs
- Local craftsmen

**2. Buyers:**

- General public who want to shop online
- Local product seekers
- Millennials and Gen Z who are used to online shopping

### Functional Requirements

#### 5.1 User Management

##### 5.1.1 User Registration

- **Priority**: High
- Description\*\*: Users can register with email or phone number
- **User Story**: As a new user, I would like to register with my email or phone number
  in order to use the "Toko Kita" app.
- **Acceptance Criteria**:
  - User can register using email or phone number
  - The system sends a verification code via email or SMS
  - Users can choose the role of buyer or seller
  - The system stores user data securely
  - User receives notification of successful registration

##### 5.1.2 User Login

- **Priority**: High
- Description: User can login with email/phone number and password.
- **User Story**: As a registered user, I would like to login with my email/phone number
  and password in order to access my account.
- **Acceptance Criteria**:
  - User can login with email/phone number and password
  - The system provides a "forgot password" feature
  - The system displays a clear error message if login fails
  - The system provides a "remember me" option.
  - The system records the last login time

##### 5.1.3 Profile Management

- **Priority**: Medium
- Description: Users can manage their profile information
- **User Story**: As a user, I want to manage my profile information so that my
  data is always up to date
- Acceptance Criteria\*\*:
  - Users can change their name, profile picture, and contact information
  - User can add multiple shipping addresses
  - User can change password
  - Seller can add store information (name, logo, description)
  - System confirms data changes with verification

#### 5.2 Product Management

##### 5.2.1 Add Product

- **Priority**: High
- Description\*\*: Sellers can add products with description, image, and price
- **User Story**: As a seller, I want to add products with full
  descriptions, images, and prices so that buyers can see and buy my products
- Acceptance Criteria\*\*:
  - Seller can upload at least 5 product images
  - Seller can enter product description up to 1000 characters
  - Seller can specify price, discount, and product variation
  - Seller can select product categories and subcategories
  - Seller can specify product stock for each variation
  - Seller can preview products before publishing

##### 5.2.2 Edit and Delete Products

- **Priority**: High
- Description\*\*: Sellers can edit and delete products that have been published
- **User Story**: As a seller, I want to edit and delete products so that
  product information is always accurate.
- Acceptance Criteria
  - Seller can edit all product information
  - Seller can temporarily deactivate products
  - Seller can delete products that are no longer for sale
  - The system keeps a history of product changes
  - Buyers cannot purchase products that have been deleted

##### 5.2.3 View Product Catalog

- **Priority**: High
- Description\*\*: Buyers can view the product catalog by category or search.
- **User Story**: As a buyer, I want to view the product catalog by category
  or search in order to find the product I want
- **Acceptance Criteria**:
  - Buyers can browse products by category and subcategory
  - Buyers can search for products based on keywords
  - Buyer can filter products by price, rating, location, and discount
  - Buyers can sort products by popularity, price, newest
  - The system displays product images, prices, discounts, and ratings in the catalog
  - The system displays "Bestseller" and "Promo" labels on relevant products

##### 5.2.4 Product Details

- **Priority**: High
- Description: Buyers can view full product details
- **User Story**: As a buyer, I want to see full product details so that
  can make an informed purchasing decision.
- **Acceptance Criteria**:

  - The system displays all product images with zoom feature
  - The system displays product descriptions, specifications, and variations
  - System displays stock availability information
  - The system displays product reviews and ratings
  - Buyers can share products to social media
  - The system displays related or recommended products

  #### 5.3 Transaction Management

##### 5.3.1 Add to Shopping Cart

- **Priority**: High
- Description\*\*: Buyers can add products to the shopping cart
- **User Story**: As a buyer, I would like to add products to my
  shopping cart so that I can buy multiple products at once.
- **Acceptance Criteria**:
  - Buyer can add products to shopping cart
  - Buyer can select product variations before adding to cart
  - Buyer can change the number of products in the cart
  - Shopper can remove products from cart
  - The system saves the user's shopping cart even if the user exits the application
  - The system displays the total price of the products in the cart
  - The system provides a notification if adding a product that is already in the cart

##### 5.3.2 Checkout and Payment Process

- **Priority**: High
- Description: Buyers can checkout and pay with various online payment methods
- **User Story**: As a buyer, I would like to checkout and pay with
  my chosen payment method in order to complete the purchase.
- **Acceptance Criteria**:
  - Buyer can select the products to be checkedout
  - Buyer can enter or select a shipping address
  - Buyer can choose a shipping method from several options
  - Buyer can choose payment method (bank transfer, e-wallet, QRIS, credit
    card, COD)
  - The system calculates the total shopping including shipping fees and taxes
  - The system provides an estimated delivery time
  - Buyers can use promo codes or vouchers
  - The system confirms the payment in real-time
  - System sends notification and invoice after successful payment

##### 5.3.3 View and Manage Orders (Buyer)

- **Priority**: Medium
- Description\*\*: Buyers can view and manage their orders
- **User Story**: As a buyer, I want to view and manage my orders so that
  can track the order status and take necessary actions
- **Acceptance Criteria**:
  - Buyers can view a list of active and completed orders
  - Buyer can view details of each order
  - Buyer can cancel unprocessed orders
  - Buyer can confirm receipt of goods
  - Buyers can return items (return) with reasons
  - Buyers can download invoices for each order
  - The system displays order status in real-time

##### 5.3.4 Manage Order (Seller)

- **Priority**: High
- Description\*\*: Seller can manage incoming orders
- **User Story**: As a seller, I want to manage incoming orders in order to
  process orders efficiently
- **Acceptance Criteria**:
  - Seller can view the list of new orders and their status
  - Seller can change the order status (processed, shipped, completed)
  - Seller can enter the shipping receipt number
  - Merchant can print shipping labels
  - Merchant can approve or reject cancellation or return requests
  - Seller receives notifications for each order status change
  - The system provides an export feature of order data in CSV format

#### 5.4 Review and Rating Management

##### 5.4.1 Give Reviews and Ratings

- **Priority**: Medium
- Description\*\*: Buyers can review and rate products
- **User Story**: As a buyer, I would like to review and rate products so I can
  share my experience with other potential buyers.
- **Acceptance Criteria**:
  - Buyers can rate 1-5 stars
  - Buyers can write reviews up to 500 characters
  - Buyers can upload a maximum of 3 photos of the purchased product
  - Buyers can only leave reviews on products that have been received
  - Buyers can edit reviews within 24 hours of posting
  - The system displays a "Verified Purchase" label on reviews from
    buyers who have proven to purchase the product
  - Sellers can respond to buyer reviews

##### 5.4.2 Manage and Moderate Reviews

- **Priority**: Low
- Description\*\*: Admins can manage and moderate reviews
- **User Story**: As an admin, I would like to manage and moderate reviews to keep the content of
  high quality and in line with platform rules.
- **Acceptance Criteria**:
  - Admins can view all reported reviews
  - Admins can remove reviews that violate the rules
  - Admins can send warnings to users
  - System automatically filters out inappropriate words
  - Buyers and sellers can report inappropriate reviews

#### 5.5 Communication

##### 5.5.1 Chat with Seller

- **Priority**: Medium
- Description\*\*: Buyers can interact with sellers via chat
- **User Story**: As a buyer, I want to interact with sellers via chat so that
  can ask for product details before buying
- **Acceptance Criteria**:
  - Buyers can send text messages to sellers
  - Buyers can send images in chat
  - Buyer can inquire about specific product availability
  - Buyer can access the chat from the product page or store page
  - The system saves the chat history
  - The system displays the seller's online/offline status
  - The system sends a notification when there is a new message
  - Sellers can view and respond to chats from buyers
  - Sellers can use template messages for general inquiries

##### 5.5.2 New Order Notification

- **Priority**: High
- Description\*\*: Sellers get notified when there is a new order
- **User Story**: As a seller, I want to be notified when there is a new order
  so that I can process the order immediately
- Acceptance Criteria\*\*:
  - Seller receives a push notification when there is a new order
  - Seller receives an email notification for new orders
  - The system displays the order details in the notification
  - Merchant can click on the notification to view the order details
  - Notifications appear in real-time
  - Merchant can set notification preferences (push, email, SMS)

##### 5.5.3 Notification System

- **Priority**: Medium
- Description: The system provides notifications for important activities
- **User Story**: As a user, I would like to receive notifications for important activities on
  to stay up-to-date.
- **Acceptance Criteria**:
  - The system sends notifications for order status changes
  - The system sends notifications for promotions and discounts
  - The system sends notifications for chat activities
  - System sends notification for successful/failed payment
  - User can set notification preferences
  - User can view notification history
  - The system categorizes notifications by category

#### 5.6 Inventory Management

##### 5.6.1 Product Stock Management

- **Priority**: Medium
- Description\*\*: Sellers can manage their product stock
- **User Story**: As a seller, I want to manage product stock so that
  information on product availability is always accurate
- **Acceptance Criteria**:
  - Seller can update product stock quantity for each variation
  - System automatically reduces stock when products are sold
  - The system provides alerts when stock reaches the minimum limit
  - Merchant can set minimum stock for notification
  - Seller can set product status (available/unavailable/pre-order)
  - System prevents purchase of products that are out of stock
  - Merchant can import/export stock data via CSV file
  - System provides stock change log

##### 5.6.2 Product Variety Management

- **Priority**: Medium
- Description\*\*: Seller can manage product variations
- **User Story**: As a seller, I want to manage product variations so that buyers can
  choose the appropriate option
- **Acceptance Criteria**:
  - Seller can add up to 3 types of variations (for example: size, color,
    model)
  - Seller can set a different price for each combination of variations
  - Seller can specify stock for each variation combination
  - Seller can upload images for each variation
  - The system displays all variation options to the buyer
  - Buyers can easily choose a combination of variations

#### 5.7 Analytics and Reports

##### 5.7.1 Seller Dashboard

- **Priority**: High
- Description: Sellers have a dashboard to view sales reports and manage
  products
- **User Story**: As a seller, I would like to have a dashboard to view
  sales reports and manage products in order to monitor my business performance
- Acceptance Criteria\*\*:
  - Dashboard displays daily, weekly, and monthly sales summary
  - Dashboard displays sales trend graph with period filters
  - Dashboard displays best selling products and most popular categories
  - Dashboard displays gross and net revenue (after commission)
  - Dashboard displays percentage growth compared to the previous
    period
  - Dashboard displays buyer distribution map
  - Sellers can export reports in CSV/PDF/Excel format
  - Dashboard displays store visitor and conversion statistics

##### 5.7.2 Admin Report

- **Priority**: Medium
- Description\*\*: Admins have access to platform reports
- **User Story**: As an admin, I would like to have access to platform reports in order to
  monitor overall business performance
- Acceptance Criteria\*\*:
  - Admin can see the total transaction and transaction value
  - Admin can see the number of active users (sellers and buyers)
  - Admin can view best selling categories and products
  - Admin can view platform commission reports
  - Admin can view user growth statistics
  - Admins can view seller performance reports
  - Admin can export all reports
  - Reports can be filtered by time period

#### 5.8 Security

##### 5.8.1 System Security and Data Privacy

- **Priority**: High
- Description: The system must ensure the security of user and transaction data
- **User Story**: As a user, I want my personal and transaction data to be protected
  to avoid misuse of data
- **Acceptance Criteria**:
  - The system encrypts user and transaction data with industry standards
  - The system implements two-factor authentication for login and important transactions
  - The system stores passwords in encrypted (hashed) form
  - System logs all login activities and sensitive actions
  - The system detects and prevents suspicious activity
  - System performs regular security updates
  - The system ensures compliance with data privacy regulations (PDP Law)
  - The system provides privacy control to users

##### 5.8.2 Access Rights Management

- **Priority**: High
- Description: The system manages user access rights based on roles
- **User Story**: As an admin, I want the system to manage the access rights of
  users based on roles so that data security is maintained.
- **Acceptance Criteria**:
  - System defines roles (admin, seller, buyer, moderator)
  - The system restricts feature access based on role
  - Admin can manage and change user access rights
  - The system records all access rights changes
  - The system applies the principle of minimum necessary access rights

#### 5.9 Promotion and Marketing

##### 5.9.1 Promotion and Discount Feature

- **Priority**: Low
- Description\*\*: Sellers can create product promotions and discounts
- **User Story**: As a seller, I want to create product promotions and discounts so that
  can increase sales
- **Acceptance Criteria**:
  - Seller can create percentage or nominal discounts
  - Sellers can create promo codes with usage restrictions
  - Sellers can create bundling promotions (buy 1 get 1 free, etc)
  - Merchant can create tiered promotions (buy more discount more
    )
  - Merchant can set promotion period (start and end date)
  - The system automatically calculates the price after discount
  - The system displays the promotion banner on the shop page
  - Buyers can use promo codes at checkout
  - The system displays the remaining promotion time to create urgency

##### 5.9.2 Loyalty Program

- **Priority**: Low
- Description: The platform provides a loyalty program for buyers
- **User Story**: As a shopper, I want to get rewarded for my shopping so that
  gets added value
- **Acceptance Criteria**:
  - Shoppers earn points for every purchase
  - Shoppers can redeem points for vouchers or discounts
  - Shoppers can view their points history and voucher usage
  - The system displays the buyer's level status (regular, silver, gold, platinum)
  - The system provides different benefits for each level
  - Sellers can participate in the platform's loyalty program

#### 5.10 Integration

##### 5.10.1 Integration with Delivery Service

- **Priority**: Medium
- Description\*\*: The system integrates with the delivery service to automate the
  process of delivery
- **User Story**: As a seller and buyer, I would like the system to integrate with
  delivery service to automate the delivery and tracking process.
- **Acceptance Criteria**:
  - The system is integrated with at least 5 delivery services (JNE, J&T, SiCepat,
    Pos Indonesia, Anteraja)
  - System can automatically calculate shipping cost based on weight,
    dimensions, and distance
  - The system can compare rates from various delivery services
  - The system can generate delivery receipt numbers automatically
  - Buyers can track real-time delivery status in the app
  - System sends notification of shipment status changes
  - Sellers can print shipping labels directly from the dashboard

##### 5.10.2 Integration with Payment Gateway

- **Priority**: High
- Description: The system is integrated with various payment gateways
- **User Story**: As a user, I want to have a wide selection of
  secure and convenient payment methods
- Acceptance Criteria\*\*:
  - System integrated with at least 3 payment gateways (Midtrans, Xendit, Doku)
  - System supports various payment methods (bank transfer, credit card,
    e-wallet, QRIS, installment)
  - System verifies payment in real-time
  - The system handles refunds and cancellations automatically
  - The system stores payment data securely according to PCI DSS standards
  - The system provides detailed financial transaction reports

##### 5.10.3 Integration with Social Media

- **Priority**: Low
- Description\*\*: The system integrates with social media platforms
- **User Story**: As a user, I want to be able to share and connect with my social
  media
- **Acceptance Criteria**:
  - User can login using social media account (Google, Facebook)
  - Users can share products to social media
  - Merchant can integrate store with Facebook/Instagram shop
  - System can import product catalog to social media
  - System tracks click-through rate from social media

### Non-Functional Requirements

#### 6.1 Performance

- Page load time is less than 3 seconds with normal internet connection
- Maximum API response time of 500ms
- System can handle at least 1000 simultaneous transactions
- Database can store up to 10 million products
- Optimized bandwidth usage for users with limited connection
- Image optimization to speed up loading time
- Implementation of caching to improve performance
- Automatic database backup every 6 hours

#### 6.2 Security

- Implementation of HTTPS for all communications
- Encryption of user and transaction data with AES-256
- Implementation of token-based authentication
- Protection against SQL injection, XSS, and CSRF
- Logging of activity logs for sensitive actions
- Strong password policy (minimum 8 characters, combination of letters, numbers, symbols)
- Account blocking after multiple failed login attempts
- Compliance with PCI DSS security standards for payment transactions
- Periodic security audits

#### 6.3 Scalability

- Microservices architecture for easy scaling
- Load balancing implementation for load distribution
- Auto-scaling based on server load
- Use of CDN for static content
- System can handle up to 100% increase in users in 6 months
- Distributed database to handle data growth

#### 6.4 Availability

- Uptime of at least 99.9% (less than 8.76 hours of downtime per year)
- Implementation of failover and redundancy
- Scheduled off-peak maintenance
- Automatic notification of system issues
- 24/7 system performance monitoring
- Disaster recovery plan with RPO < 1 hour and RTO < 4 hours

#### 6.5 Usability

- Intuitive and easy-to-use user interface
- Responsive design for all screen sizes
- Support for users with disabilities (accessibility)
- User guides and tooltips for complex features
- Consistency of design throughout the application
- Minimal training time for new users
- Support for swipe gestures in mobile apps
- Fast and accurate search features

#### 6.6 Compatibility

- Compatible with major browsers (Chrome, Firefox, Safari, Edge)
- Compatible with desktop operating systems (Windows, MacOS, Linux)
- Compatible with mobile operating systems (Android 7.0+, iOS 11.0+)
- Support for different screen resolutions
- Automatic adaptation to screen orientation (portrait/landscape)
- Support for dark mode

#### 6.7 Maintenance

- Complete code documentation
- Modular architecture for easy maintenance
- Automated testing (unit tests, integration tests)
- Versioning for API
- Regular updates without service interruption
- Monitoring system for performance and errors

#### 6.8 Internationalization

- Support for Indonesian as the primary language
- Preparation for additional language support in the future
- Time, date, and currency formats according to Indonesian standards
- Support for currency conversion (optional)

### User Interface Requirements

#### 7.1 Home Page

- Rotating promotional banner (carousel)
- Product categories with icons
- Featured and best-selling products
- Popular stores
- Product recommendations based on shopping history
- Promotion and discount banners

#### 7.2 Category Page

- Filter and sort products
- Grid and list view for product display
- Breadcrumb for navigation
- Custom labels for discounted products, bestsellers, etc.
- Pagination or infinite scroll

#### 7.3 Product Detail Page

- Product photo gallery with zoom
- Complete product information
- Product variation selection
- “Add to Cart” and “Buy Now” buttons
- Product review section
- Related products
- Seller information

#### 7.4 Shopping Cart

- List of products with thumbnail images
- Option to change quantity
- Option to delete products
- Price summary (subtotal, tax, shipping cost, total)
- "Continue Shopping" and "Checkout" buttons

#### 7.5 Checkout page

- Delivery address form
- Choice of shipping method
- Choice of payment method
- Order summary
- Promo code field
- Order confirmation

#### 7.6 Seller Dashboard

- Summary widgets (sales, revenue, new orders)
- Sales graph
- New order list and status
- Product management
- Store statistics
- Store settings

### Technical Requirements

#### 8.1 System Architecture

- Microservices-based architecture
- RESTful API for communication between front-end and back-end
- Single page application (SPA) for front-end
- Relational database for structured data
- NoSQL database for unstructured data (reviews, logs)

#### 8.2 Technology

- Front-end: React.js, React Native (for mobile apps)
- Back-end: Node.js/Express.js or Laravel/PHP
- Database: PostgreSQL, MongoDB
- Caching: Redis
- Search Engine: Elasticsearch
- Message Queue: RabbitMQ
- CDN: Cloudflare or AWS CloudFront
- Hosting: AWS, Google Cloud, or Azure

### Project Budget and Limitations

- Project Budget: IDR 500,000,000
- Timeframe: 6 months
- Development Team: 5 people (1 Project Manager, 2 Backend Developer, 1 Frontend
  Developer, 1 UI/UX Designer)

### Project Acceptance Criteria

- All high and medium priority functional requirements are met
- Non-functional requirements are met, especially related to performance and security
- User testing with a minimum of 30 users shows an 80% satisfaction rate
- Application can handle a minimum of 1000 simultaneous transactions without performance degradation
- Full documentation available (user guide, technical documentation, API
  documentation)
- Passed third-party security testing

### Schedule and Milestones

#### Milestone 1: Design and Planning (1 month)

- Requirements finalization
- UI/UX design
- Database design
- Design approval

#### Milestone 2: Initial Development (2 months)

- Basic feature development (user management, product catalog)
- Payment gateway integration
- Delivery service integration
- Alpha testing

#### Milestone 3: Advanced Development (2 months)

- Additional feature development (reviews, chat, notifications)
- Dashboard and analytics implementation
- Beta testing
- Performance optimization

#### Milestone 4: Finalize and Launch (1 month)

- User testing
- Bug fixes
- Final optimization
- Documentation
- Launch

### Risk and Mitigation

#### Technical Risks

- Risks: Integration issues with payment gateway Mitigation: Start integration early,
  prepare alternative payment gateway
- Risk: Slow performance under high load Mitigation: Load testing early on, design
  scalable architecture

#### Business Risk

- Risk: Lack of adoption from sellers Mitigation: Onboarding program and incentives for early
  sellers
- Risk: Competition with established e-commerce platforms Mitigation: focus on local MSMEs and product uniqueness

### Glossary

- MSMES: Micro, Small, and Medium Enterprises
- COD: Cash on Delivery
- QRIS: Quick Response Code Indonesian Standard
- API: Application Programming Interface
- CDN: Content Delivery Network
- SPA: Single Page Application
- RPO: Recovery Point Objective
- RTO: Recovery Time Objective
