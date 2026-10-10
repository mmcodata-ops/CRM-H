import json
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

from .models import Account, Interaction, Invoice, Payment, Shipment, Attachment, SaleRecord, MasterOrder, DebitNote, DebitNoteItem, Lead

@admin.action(description="⚠️ WIPE ENTIRE TABLE (All Pages)")
def wipe_entire_table(modeladmin, request, queryset):
    count = modeladmin.model.objects.count()
    modeladmin.model.objects.all().delete()
    from django.contrib import messages
    messages.success(request, f"Successfully wiped all {count} records.")

class SaleRecordResource(resources.ModelResource):
    sale_date = fields.Field(attribute='sale_date', column_name='SALE DATE')
    party = fields.Field(attribute='party', column_name='PARTY')
    rf_no = fields.Field(attribute='rf_no', column_name='RF. NO')
    invoice_no = fields.Field(attribute='invoice_no', column_name='INVOICE NO')
    master_invoice_no = fields.Field(attribute='master_invoice_no', column_name='MASTER INVOICE NO')
    item = fields.Field(attribute='item', column_name='ITEM')
    order_no = fields.Field(attribute='order_no', column_name='ORDER NO.')
    purchase_order_no = fields.Field(attribute='purchase_order_no', column_name='PURCHASE ORDER NO.')
    sale_ch_no = fields.Field(attribute='sale_ch_no', column_name='SALE CH. NO.')
    value = fields.Field(attribute='value', column_name='VALUE')
    
    def before_import_row(self, row, **kwargs):
        cleaned_row = {str(k).strip(): v for k, v in row.items()}
        row.clear()
        row.update(cleaned_row)
        if 'VALUE' in row and isinstance(row['VALUE'], str):
            row['VALUE'] = row['VALUE'].replace('$', '').replace(',', '').strip()

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row.get('ORDER NO.') or str(row.get('ORDER NO.')).strip() == '':
            return True
        return super().skip_row(instance, original, row, import_validation_errors=import_validation_errors)

    class Meta:
        model = SaleRecord
        skip_unchanged = False


@admin.register(SaleRecord)
class SaleRecordAdmin(ImportExportModelAdmin):
    actions = [wipe_entire_table]
    resource_classes = [SaleRecordResource]
    list_display = ('sale_date', 'party', 'rf_no', 'invoice_no', 'master_invoice_no', 'item', 'value')
    list_filter = ('party', 'sale_date')
    search_fields = ('invoice_no', 'master_invoice_no', 'item', 'order_no')


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

    def before_import_row(self, row, **kwargs):
        cleaned_row = {str(k).strip(): v for k, v in row.items()}
        row.clear()
        row.update(cleaned_row)

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row.get('Order No.') or str(row.get('Order No.')).strip() == '':
            return True
        return super().skip_row(instance, original, row, import_validation_errors=import_validation_errors)

    class Meta:
        model = MasterOrder
        skip_unchanged = False

@admin.register(MasterOrder)
class MasterOrderAdmin(ImportExportModelAdmin):
    actions = [wipe_entire_table]
    resource_classes = [MasterOrderResource]
    list_display = ('order_no', 'buyer_name', 'order_date', 'status', 'sku', 'price')
    list_filter = ('status', 'portals')
    search_fields = ('order_no', 'buyer_name', 'sku', 'email')


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage', 'email', 'balance', 'created_at')
    list_filter = ('stage', 'created_at')
    search_fields = ('name', 'email')
    inlines = [InteractionInline, AttachmentInline]

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('account', 'interaction_type', 'date')
    list_filter = ('interaction_type', 'date')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'amount', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'amount', 'invoice', 'date')
    list_filter = ('date', 'account')

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'tracking_number', 'carrier', 'status')

class DebitNoteItemInline(admin.TabularInline):
    model = DebitNoteItem
    extra = 1

@admin.register(DebitNote)
class DebitNoteAdmin(admin.ModelAdmin):
    list_display = ('voucher_no', 'party_name', 'date', 'grand_total')
    search_fields = ('voucher_no', 'party_name')
    inlines = [DebitNoteItemInline]

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    change_list_template = 'admin/erp/lead/change_list.html'

    def changelist_view(self, request, extra_context=None):
        total_leads = Lead.objects.count()
        converted_leads = Lead.objects.filter(status='CONVERTED').count()
        
        source_data = Lead.objects.values('source').annotate(count=Count('id'))
        status_data = Lead.objects.values('status').annotate(count=Count('id'))
        
        extra_context = extra_context or {}
        extra_context['dashboard_data'] = {
            'total_leads': total_leads,
            'converted_leads': converted_leads,
            'sources': {item['source']: item['count'] for item in source_data},
            'statuses': {item['status']: item['count'] for item in status_data},
        }
        return super().changelist_view(request, extra_context=extra_context)

    list_display = ('first_name', 'last_name', 'company', 'source', 'status', 'created_at')
    list_filter = ('source', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'company')
    actions = [wipe_entire_table]
