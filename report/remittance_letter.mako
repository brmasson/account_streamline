<style type="text/css">
${css}

.line td {
    text-align: center;
}

.remittance_letter_bottom, .remittance_letter_company_bottom {
	margin-top: 30px;
}

.remittance_letter_bottom {
    padding: 10px 10px 10px 10px;
    border: 1px #000000 solid;
}

.remittance_letter_message {
    clear: both;
    margin-top: 40px;
    margin-bottom: 40px;
}

.remittance_letter_total {
    margin-top: 30px;
    padding: 10px 10px 10px 10px;
    border: 1px #000000 solid;
    text-align: right;
}

.remittance_letter_voucher_name {
	clear: both;
    margin-top: 40px;
    margin-bottom: 40px;
}

</style>

%for object in objects:
<% setLang(object.partner_id.lang) %>

<div class="address">
    <div class="addressright">
        <table class="recipient">
            <tr><th class="addresstitle">${ _("Supplier address") } :</th></tr>
            %if object.partner_id.parent_id:
            <tr><td class="name">${object.partner_id.parent_id.name or ''}</td></tr>
            <% address_lines = object.partner_id.contact_address.split("\n")[1:] %>
            %else:
            <% address_lines = object.partner_id.contact_address.split("\n") %>
            %endif
            <tr><td class="name">${object.partner_id.title and object.partner_id.title.name or ''} ${object.partner_id.name }</td></tr>
            %for part in address_lines:
                %if part:
                <tr><td>${part}</td></tr>
                %endif
            %endfor
        </table>
    </div>
    <div class="addressleft">
        <table class="shipping">
            <tr><th class="addresstitle">${ _("Shipping address") } :</th></tr>
            %if object.company_id.partner_id.parent_id:
            <tr><td class="name">${object.company_id.partner_id.parent_id.name or ''}</td></tr>
            <% address_lines = object.company_id.partner_id.contact_address.split("\n")[1:] %>
            %else:
            <% address_lines = object.company_id.partner_id.contact_address.split("\n") %>
            %endif
            <tr><td class="name">${object.company_id.partner_id.title and object.company_id.partner_id.title.name or ''} ${object.company_id.partner_id.name }</td></tr>
            %for part in address_lines:
                %if part:
                <tr><td>${ part }</td></tr>
                %endif
            %endfor
            <tr><td>${object.partner_id.email}</td></tr>
       </table>
    </div>
</div>

<!-- Using h2 as the font-size property doesn't seem to affect divs... -->
<h2 class="remittance_letter_voucher_name">${ object.name }</h2>

<h2 class="remittance_letter_message">${ top_message(object) }</h2>

<table class="list_table">
    <thead>
        <tr>
            <th>${ _('Transaction reference') }</th>
            <th>${ _('Invoice date') }</th>
            <th>${ _('Debit/Credit') }</th>
            <th>${ _('Currency') }</th>
            <th class="amount">${ _('Amount') }</th>
        </tr>
    </thead>
    <tbody>
        %for line in object.line_dr_ids:
        <tr class="line">
            <td>${ line.name }</td>
            <td>${ line.date_original }</td>
            <td>${ debit_credit(line) }</td>
            <td>${ line.currency_id.name }</td>
            <td class="amount">${ format_amount(line.amount, object) }</td>
        </tr>
        %endfor
    </tbody>
</table>

<h2 class="remittance_letter_total">${ _('Total:') } ${ format_amount(object.amount, object) }</h2>

<!-- Voucher-specific bottom information. -->
${ object.remittance_letter_bottom }

<!-- Company-specific bottom information. -->
<h2 class="remittance_letter_company_bottom">${ bottom_message(object) }</h2>

%endfor

