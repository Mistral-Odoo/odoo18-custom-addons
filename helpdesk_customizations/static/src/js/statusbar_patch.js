/** @odoo-module **/

import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";
import { patch } from "@web/core/utils/patch";

/**
 * Patch selectItem to handle save errors gracefully.
 *
 * The original selectItem() calls record.update() (which optimistically
 * changes the UI) then record.save(). If the save fails (e.g. UserError
 * from server validation), the UI is left in an inconsistent state showing
 * the wrong stage with fields appearing editable.
 *
 * This patch uses the onError callback supported by record._save(), the
 * same mechanism Odoo's FormController uses. When save fails:
 *  1. discard() reverts record._changes and record.data synchronously
 *  2. record._load() reloads fresh data from the server, guaranteeing
 *     the record state matches the database (same as _save()'s own
 *     error handling when isInEdition=false)
 *  3. Promise.reject() propagates the error to Odoo's error service
 *     which shows the standard error dialog
 *  4. selectItem() resolves normally, letting OWL re-render cleanly
 */
patch(StatusBarField.prototype, {
    async selectItem(item) {
        const { name, record } = this.props;
        const value = this.field.type === "many2one" ? [item.value, item.label] : item.value;
        await record.update({ [name]: value });
        await record.save({
            onError: async (error, { discard }) => {
                discard();
                await record._load({});
                Promise.reject(error);
            },
        });
    },
});
