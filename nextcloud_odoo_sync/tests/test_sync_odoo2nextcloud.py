from unittest.mock import MagicMock, patch
from odoo.addons.nextcloud_odoo_sync.tests.test_sync_common import TestSyncNextcloud
from odoo.addons.nextcloud_odoo_sync.models.nextcloud_caldav import Nextcloudcaldav
from odoo.addons.nextcloud_odoo_sync.models.nc_sync_user import NcSyncUser
from caldav.objects import Calendar, Event


class TestSyncOdoo2Nextcloud(TestSyncNextcloud):
    def setUp(self):
        super().setUp()

    def test_update_nextcloud_events(self):
        cal_event = self.create_nextcloud_event()
        with patch.object(
            Nextcloudcaldav,
            "get_user_calendar",
            MagicMock(spec=Nextcloudcaldav.get_user_calendar),
        ) as mock_get_user_calendar:
            mock_get_user_calendar.return_value = cal_event.parent
            with patch.object(
                Calendar, "save_event", MagicMock(spec=Calendar.save_event)
            ) as mock_save_event:
                mock_save_event.return_value = cal_event
                with patch.object(
                    Event, "save", MagicMock(spec=Calendar.save)
                ) as mock_save:
                    mock_save.return_value = True
                    with patch.object(
                        NcSyncUser,
                        "get_nc_event_hash_by_uid",
                        MagicMock(spec=NcSyncUser.get_nc_event_hash_by_uid),
                    ) as mock_get_nc_event_hash_by_uid:
                        mock_get_nc_event_hash_by_uid.return_value = "test_hash"
                        nextcloud_caldav_obj = self.env["nextcloud.caldav"]
                        params = self.get_params()
                        params2 = params.copy()
                        nextcloud_caldav_obj.update_nextcloud_events(
                            params["sync_user_id"],
                            params["nc_events_dict"],
                            **params["params"]
                        )
                        od_event = self.env["calendar.event"].search_read(
                            [
                                (
                                    "id",
                                    "=",
                                    params2["nc_events_dict"]["create"][0][
                                        "od_event"
                                    ].id,
                                )
                            ]
                        )
                        self.assertNextcloudEventCreated(od_event)