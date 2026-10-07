from django.db import models

class Account(models.Model):
    STAGE_CHOICES = (
        ('LEAD', 'Lead (New)'),
        ('CONTACTED', 'Contacted'),
        ('NEGOTIATING', 'Negotiating'),
        ('ACTIVE', 'Active Account'),
        ('INACTIVE', 'Inactive'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='LEAD')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def balance(self):
        total_invoiced = sum(i.amount for i in self.invoices.all())
        total_paid = sum(p.amount for p in self.payments.all())
        return total_invoiced - total_paid

class Interaction(models.Model):
    TYPE_CHOICES = (
        ('EMAIL', 'Email'),
        ('CALL', 'Phone Call'),
        ('MEETING', 'Meeting'),
        ('NOTE', 'Internal Note'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='NOTE')
    notes = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_interaction_type_display()} on {self.date.strftime('%Y-%m-%d')}"

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.account.name} - ${self.amount}"

class Payment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='applied_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="If invoice is blank, this is an advance.")

    def __str__(self):
        adv = " (Advance)" if not self.invoice else ""
        return f"Payment #{self.id} - {self.account.name} - ${self.amount}{adv}"

class Shipment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Shipment #{self.id} - {self.tracking_number or 'Pending'}"

class Attachment(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.account.name}"

class SaleRecord(models.Model):
    sale_date = models.CharField(max_length=100, null=True, blank=True)
    party = models.CharField(max_length=100, blank=True, null=True, verbose_name="PARTY")
    rf_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="RF. NO")
    invoice_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="INVOICE NO")
    master_invoice_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="MASTER INVOICE NO")
    item = models.CharField(max_length=500, blank=True, null=True, verbose_name="ITEM")
    order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="ORDER NO.")
    purchase_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="PURCHASE ORDER NO.")
    sale_ch_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="SALE CH. NO.")
    value = models.CharField(max_length=100, null=True, blank=True, verbose_name="VALUE")

    def __str__(self):
        return f"{self.invoice_no} - {self.item}"

class MasterOrder(models.Model):
    no_of_late = models.CharField("NO OF LATE", max_length=100, blank=True, null=True)
    remarks = models.TextField("REMARKS", blank=True, null=True)
    ref_id = models.CharField("Ref# ID", max_length=100, blank=True, null=True)
    portals = models.CharField("Portals", max_length=100, blank=True, null=True)
    order_no = models.CharField("Order No.", max_length=100, blank=True, null=True)
    buyer_name = models.CharField("Buyer Name", max_length=255, blank=True, null=True)
    picture = models.CharField("Picture", max_length=500, blank=True, null=True)
    order_date = models.CharField("Order Date", max_length=100, blank=True, null=True)
    quantity = models.CharField("Quantity", max_length=100, blank=True, null=True)
    material = models.CharField("COTTON/JUTE", max_length=100, blank=True, null=True)
    size = models.CharField("SIZE", max_length=100, blank=True, null=True)
    tassel_fringes = models.CharField("Tassel/Fringes", max_length=100, blank=True, null=True)
    expected_date = models.CharField("Expected date", max_length=100, blank=True, null=True)
    status = models.CharField("Status", max_length=100, blank=True, null=True)
    hold_cancelled_date = models.CharField("HOLD/ CANCELLED DATE", max_length=100, blank=True, null=True)
    dispatch_date = models.CharField("Dispatch Date", max_length=100, blank=True, null=True)
    sku = models.CharField("SKU", max_length=100, blank=True, null=True)
    photos = models.CharField("Photos", max_length=500, blank=True, null=True)
    delivery_date = models.CharField("Delivery Date", max_length=100, blank=True, null=True)
    complete_name = models.CharField("Complete Name", max_length=255, blank=True, null=True)
    street = models.CharField("street", max_length=255, blank=True, null=True)
    street2 = models.CharField("Street2", max_length=255, blank=True, null=True)
    city = models.CharField("City", max_length=100, blank=True, null=True)
    state = models.CharField("State", max_length=100, blank=True, null=True)
    zip_code = models.CharField("Zip", max_length=50, blank=True, null=True)
    country = models.CharField("Country", max_length=100, blank=True, null=True)
    phone = models.CharField("Phone", max_length=100, blank=True, null=True)
    email = models.CharField("Email", max_length=255, blank=True, null=True)
    tags = models.CharField("Tags", max_length=255, blank=True, null=True)
    company = models.CharField("Company", max_length=255, blank=True, null=True)
    company_type = models.CharField("Company Type", max_length=100, blank=True, null=True)
    gst_treatment = models.CharField("GST Treatment", max_length=100, blank=True, null=True)
    products = models.TextField("PRODUCTS", blank=True, null=True)
    size_2 = models.CharField("Size 2", max_length=100, blank=True, null=True)
    pcs = models.CharField("Pcs.", max_length=100, blank=True, null=True)
    price = models.CharField("Price", max_length=100, blank=True, null=True)
    column_2 = models.CharField("Column 2", max_length=100, blank=True, null=True)
    hsn_code = models.CharField("HSN CODE", max_length=100, blank=True, null=True)
    dtp_payment_received = models.CharField("DTP PAYMENT RECEIVED", max_length=100, blank=True, null=True)
    check_by = models.CharField("CHECK BY", max_length=100, blank=True, null=True)
    shipping_date = models.CharField("SHIPPING DATE", max_length=100, blank=True, null=True)
    status_2 = models.CharField("STATUS 2", max_length=100, blank=True, null=True)
    est_date_1 = models.CharField("EST DATE 1", max_length=100, blank=True, null=True)
    est_date_2 = models.CharField("EST DATE 2", max_length=100, blank=True, null=True)
    rcvd_date = models.CharField("Rcvd. Date", max_length=100, blank=True, null=True)
    rcvd_paper_date = models.CharField("Rcvd. Paper date", max_length=100, blank=True, null=True)
    send_paper_date = models.CharField("SEND PAPER DATE", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_no} - {self.buyer_name}"
