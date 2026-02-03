-- Run this on the Odoo database ONLY if you get KeyError: 'ics.tender'
-- and the ics_tender_management module is not (yet) installed.
-- This removes orphan mail activities and messages that reference ics.tender.

BEGIN;

-- Remove activities on ics.tender (causes KeyError when module not loaded)
DELETE FROM mail_activity WHERE res_model = 'ics.tender';

-- Remove message references (optional; uncomment if you also get errors on mail_message)
-- DELETE FROM mail_message WHERE model = 'ics.tender';

COMMIT;
