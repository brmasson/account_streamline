from openerp.osv import fields, expression, osv
from openerp.tools.translate import _
import yaml
from lxml import etree

# account.move.line fields that don't become read-only when the account.move
# object is posted.
list_readonly_loose = [
    'date_maturity'
]
list_noreadonly = [
    'a1_id', 'a2_id', 'a3_id', 'a4_id', 'a5_id'
]

list_readonly_condition = (
    '[["move_state", "=", "posted"]]'
)
list_readonly_condition_loose = (
    '[["move_state", "=", "posted"], '
    '["reconcile_id", "!=", false]]'
)


class account_move(osv.Model):
    _name = 'account.move'

    _inherit = [
        'account.move',
        'mail.thread',
    ]

    _columns = {
        # Redefine this field to remove the read-only constraint; it is however
        # carefully propagated to line fields via attributes inserted from the
        # fields_view_get function (except for fields we want to keep
        # modifiable).
        'line_id': fields.one2many(
            'account.move.line',
            'move_id',
            'Entries'
        ),
    }

    def _analysis_control(self, cr, uid, ids, context=None):
        """This controls the account.move.line analysis dimensions settings
        set on account.account It will perform this only when attempting to
        post a complete move and will compile all errors coming from move
        lines in a single message
        """
        # move_dict = {}
        lines = []

        ans_obj = self.pool.get('analytic.structure')
        ans_ids = ans_obj.search(cr, uid,
                                 [('model_name', '=', 'account_move_line')],
                                 context=context)
        ans_br = ans_obj.browse(cr, uid, ans_ids, context=context)
        ans_dict = dict()
        for ans in ans_br:
            ans_dict[ans.ordering] = ans.nd_id.name

        for move in self.browse(cr, uid, ids, context=context):
            # line_dict = []
            for aml in move.line_id:
                dim_list = []
                if aml.account_id.t1_ctl == '1' and not aml.a1_id:
                    dim_list.append(ans_dict.get('1', 'A1').encode('utf8'))
                if aml.account_id.t2_ctl == '1' and not aml.a2_id:
                    dim_list.append(ans_dict.get('2', 'A2').encode('utf8'))
                if aml.account_id.t3_ctl == '1' and not aml.a3_id:
                    dim_list.append((ans_dict.get('3', 'A3').encode('utf8')))
                if aml.account_id.t4_ctl == '1' and not aml.a4_id:
                    dim_list.append((ans_dict.get('4', 'A4').encode('utf8')))
                if aml.account_id.t5_ctl == '1' and not aml.a5_id:
                    dim_list.append((ans_dict.get('5', 'A5').encode('utf8')))
                if dim_list:
                    # line_dict[aml.name.encode('utf8')] = dim_list
                    tmp = [aml.name.encode('utf8')]
                    tmp.append(dim_list)
                    lines += tmp
            # if lines:
                # move_dict[move.ref.encode('utf8')] = line_dict

        if lines:
            msg_analysis = _(
                "Unable to post! The following analysis codes are mandatory:"
            )
            msg_analysis += '\n'
            msg_analysis += yaml.dump(lines)
            raise osv.except_osv(_('Error!'), msg_analysis)

    def post(self, cr, uid, ids, context=None):
        """override the post method so all lines can be check against analysis
        controls
        """
        self._analysis_control(cr, uid, ids, context=context)

        return super(account_move, self).post(cr, uid, ids, context=context)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """We display analysis codes on the account.move form inserting them
        in the one2many field containing account move lines
        """
        if context is None:
            context = {}
        res = super(account_move,
                    self).fields_view_get(cr, uid, view_id=view_id,
                                          view_type=view_type,
                                          context=context,
                                          toolbar=toolbar,
                                          submenu=False)
        ans_obj = self.pool.get('analytic.structure')

        # display analysis codes only when present on a related structure,
        # with dimension name as label
        ans_ids = ans_obj.search(cr, uid,
                                 [('model_name', '=', 'account_move_line')],
                                 context=context)
        ans_br = ans_obj.browse(cr, uid, ans_ids, context=context)
        ans_dict = dict()
        for ans in ans_br:
            ans_dict[ans.ordering] = ans.nd_id.name
        if 'fields' in res and 'line_id' in res['fields']:
            doc = etree.XML(res['fields']['line_id']['views']['tree']['arch'])
            line_fields = res['fields']['line_id']['views']['tree']['fields']

            # TODO Improve how we play with the "modifiers" attribute
            # (ast.literal_eval?).

            def set_readonly(field, condition):
                """Add a readonly modifier; preserve previous ones."""
                elem = doc.xpath("//field[@name='%s']" % field)[0]
                modifiers = elem.get('modifiers')
                closing = modifiers.rfind('}')
                if closing in (-1, 1):  # no dict or empty dict
                    elem.set(
                        'modifiers',
                        '{"readonly": %s}' % condition
                    )
                else:
                    elem.set(
                        'modifiers',
                        modifiers[:closing] +
                        (', "readonly": %s' % condition) +
                        modifiers[closing:]
                    )

            def set_analytic_visibility(index):
                """Add a tree_invisible modifier; preserve previous ones."""
                elem = doc.xpath("//field[@name='a%d_id']" % index)[0]
                modifiers = elem.get('modifiers')
                closing = modifiers.rfind('}')
                if closing in (-1, 1):  # no dict or empty dict
                    elem.set('modifiers', '{"tree_invisible": %s}' %
                        str(not str(index) in ans_dict).lower())
                else:
                    elem.set('modifiers', modifiers[:closing] +
                        ', "tree_invisible": %s' %
                        str(not str(index) in ans_dict).lower() +
                        modifiers[closing:])

            user_obj = self.pool.get('res.users')
            auth_readonly_loose = user_obj.has_group(
                cr, uid, 'analytic_structure.group_ans_manager'
            )
            auth_admin = user_obj.has_group(cr, uid, 'base.group_no_one')

            # Handle fields modifiers on posted / allocated entries
            for line_field in line_fields:
                # is authorized
                if auth_readonly_loose or auth_admin:
                    # can change these when not allocated
                    # admin can also change partner_id
                    if line_field in list_readonly_loose or \
                            (auth_admin and line_field == 'partner_id'):
                        set_readonly(line_field, list_readonly_condition_loose)
                    # can always change those
                    elif line_field in list_noreadonly:
                        # do not change modifiers
                        continue
                    # other fields cannot be changed when posted
                    else:
                        set_readonly(line_field, list_readonly_condition)
                else:
                    set_readonly(line_field, list_readonly_condition)

            if 'a1_id' in line_fields:
                line_fields['a1_id']['string'] = ans_dict.get('1', 'A1')
                set_analytic_visibility(1)
            if 'a2_id' in line_fields:
                line_fields['a2_id']['string'] = ans_dict.get('2', 'A2')
                set_analytic_visibility(2)
            if 'a3_id' in line_fields:
                line_fields['a3_id']['string'] = ans_dict.get('3', 'A3')
                set_analytic_visibility(3)
            if 'a4_id' in line_fields:
                line_fields['a4_id']['string'] = ans_dict.get('4', 'A4')
                set_analytic_visibility(4)
            if 'a5_id' in line_fields:
                line_fields['a5_id']['string'] = ans_dict.get('5', 'A5')
                set_analytic_visibility(5)

            res['fields']['line_id']['views']['tree']['arch'] = (
                etree.tostring(doc)
            )
        return res


class mail_message(osv.Model):
    _inherit = 'mail.message'

    def message_read(
        self, cr, uid, ids=None, domain=None, message_unload_ids=None,
        thread_level=0, context=None, parent_id=False, limit=None
    ):
        """Override this function to include account.move.line notifications
        within account.move notification lists.

        :todo This applies to every mail.message object; maybe find a better
        solution that doesn't involve modifying objects globally.
        """

        # Example domain: [['model', '=', 'account.move'], ['res_id', '=', 7]]

        # Avoid recursion...
        if domain and ['model', '=', 'account.move.line'] not in domain:

            am_obj = self.pool.get('account.move')

            line_domain = []

            # Look for a "res_id = X" domain part.
            for domain_index, domain_part in enumerate(domain):
                if (domain_index < len(domain) - 1 and
                    domain_part == ['model', '=', 'account.move']
                ):
                    next_part = domain[domain_index + 1]
                    if next_part[0] == 'res_id' and next_part[1] == '=':

                        move_id = next_part[2]
                        line_ids = am_obj.read(
                            cr, uid,
                            move_id,
                            ['line_id'],
                            context=context
                        )['line_id']

                        line_domain = [
                            ('model', '=', 'account.move.line'),
                            ('res_id', 'in', line_ids)
                        ]

            if line_domain:
                domain = expression.OR([
                    expression.normalize_domain(line_domain),
                    expression.normalize_domain(domain)
                ])

                # Make sure our domain is applied. When "ids" is set, the
                # domain is ignored.
                ids = None

        return super(mail_message, self).message_read(
            cr, uid, ids=ids, domain=domain,
            message_unload_ids=message_unload_ids, thread_level=thread_level,
            context=context, parent_id=parent_id, limit=limit
        )
