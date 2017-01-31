bandwidth package
=====================

bandwidth.client module
---------------------------

.. automodule:: bandwidth
    :members:
    :undoc-members:
    :show-inheritance:

Calls
------
.. autoclass:: bandwidth.catapult.Client
    :members: list_calls, create_call, get_call, update_call, play_audio_to_call, send_dtmf_to_call, list_call_recordings, list_call_transcriptions, list_call_events, get_call_event, create_call_gather, get_call_gather, update_call_gather, answer_call, reject_call, hangup_call, enable_call_recording, disable_call_recording, toggle_call_recording, transfer_call


Account
-------
.. autoclass:: bandwidth.catapult.Client
    :members: get_account, get_account_transactions

Applications
------------
.. autoclass:: bandwidth.catapult.Client
    :members: list_applications, create_application, get_application, delete_application

Available Numbers
-----------------
.. autoclass:: bandwidth.catapult.Client
    :members: search_available_local_numbers, search_available_toll_free_numbers, search_and_order_local_numbers, search_and_order_toll_free_numbers

Bridges
-------
.. autoclass:: bandwidth.catapult.Client
    :members: list_bridges, create_bridge, get_bridge, update_bridge, list_bridge_calls, play_audio_to_bridge

Conferences
-----------
.. autoclass:: bandwidth.catapult.Client
    :members: create_conference, get_conference, update_conference, play_audio_to_conference, list_conference_members, create_conference_member, get_conference_member, update_conference_member, play_audio_to_conference_member, speak_sentence_to_conference_member, play_audio_file_to_conference_member, remove_conference_member, hold_conference_member, mute_conference_member, terminate_conference, hold_conference, mute_conference