import sys

new_resource = """
class MasterOrderResource(resources.ModelResource):
    no_of_late = fields.Field(attribute='no_of_late', column_name='NO OF LATE')
    remarks = fields.Field(attribute='remarks', column_name='REMARKS')
    ref_id = fields.Field(attribute='ref_id', column_name='Ref# ID')
    portals = fields.Field(attribute='portals', column_name='Portals')
    order_no = fields.Field(attribute='order_no', column_name='Order No.')
    buyer_name = fields.Field(attribute='buyer_name', column_name='Buyer Name')
    picture = fields.Field(attribute='picture', column_name='Picture')
    order_date = fields.Field(attribute='order_date', column_name='Order Date')
    quantity = fields.Field(attribute='quantity', column_name='Quantity')
    material = fields.Field(attribute='material', column_name='COTTON/JUTE')
    size = fields.Field(attribute='size', column_name='SIZE')
    tassel_fringes = fields.Field(attribute='tassel_fringes', column_name='Tassel/Fringes')
    expected_date = fields.Field(attribute='expected_date', column_name='Expected date')
    status = fields.Field(attribute='status', column_name='Status')
    hold_cancelled_date = fields.Field(attribute='hold_cancelled_date', column_name='HOLD/ CANCELLED DATE')
    dispatch_date = fields.Field(attribute='dispatch_date', column_name='Dispatch Date')
    sku = fields.Field(attribute='sku', column_name='SKU')
    photos = fields.Field(attribute='photos', column_name='Photos')
    delivery_date = fields.Field(attribute='delivery_date', column_name='Delivery Date')
    complete_name = fields.Field(attribute='complete_name', column_name='Complete Name')
    street = fields.Field(attribute='street', column_name='street')
    street2 = fields.Field(attribute='street2', column_name='Street2')
    city = fields.Field(attribute='city', column_name='City')
    state = fields.Field(attribute='state', column_name='State')
    zip_code = fields.Field(attribute='zip_code', column_name='Zip')
    country = fields.Field(attribute='country', column_name='Country')
    phone = fields.Field(attribute='phone', column_name='Phone')
    email = fields.Field(attribute='email', column_name='Email')
    tags = fields.Field(attribute='tags', column_name='Tags')
    company = fields.Field(attribute='company', column_name='Company')
    company_type = fields.Field(attribute='company_type', column_name='Company Type')
    gst_treatment = fields.Field(attribute='gst_treatment', column_name='GST Treatment')
    products = fields.Field(attribute='products', column_name='PRODUCTS')
    size_2 = fields.Field(attribute='size_2', column_name='Size')
    pcs = fields.Field(attribute='pcs', column_name='Pcs.')
    price = fields.Field(attribute='price', column_name='Price')
    column_2 = fields.Field(attribute='column_2', column_name='Column 2')
    hsn_code = fields.Field(attribute='hsn_code', column_name='HSN CODE')
    dtp_payment_received = fields.Field(attribute='dtp_payment_received', column_name='DTP PAYMENT RECEIVED')
    check_by = fields.Field(attribute='check_by', column_name='CHECK BY')
    shipping_date = fields.Field(attribute='shipping_date', column_name='SHIPPING DATE')
    status_2 = fields.Field(attribute='status_2', column_name='STATUS')
    est_date_1 = fields.Field(attribute='est_date_1', column_name='EST DATE 1')
    est_date_2 = fields.Field(attribute='est_date_2', column_name='EST DATE 2')
    rcvd_date = fields.Field(attribute='rcvd_date', column_name='Rcvd. Date')
    rcvd_paper_date = fields.Field(attribute='rcvd_paper_date', column_name='Rcvd. Paper date')
    send_paper_date = fields.Field(attribute='send_paper_date', column_name='SEND PAPER DATE')

    class Meta:
        model = MasterOrder
        skip_unchanged = True
"""

with open('erp/admin.py', 'r') as f:
    c = f.read()

c = c.replace('@admin.register(MasterOrder)', new_resource + '\n@admin.register(MasterOrder)')
c = c.replace('class MasterOrderAdmin(ImportExportModelAdmin):', 'class MasterOrderAdmin(ImportExportModelAdmin):\n    resource_class = MasterOrderResource')

with open('erp/admin.py', 'w') as f:
    f.write(c)
