from client_v2 import Client as ClientV2


creds = ('u-**********', ('t-******', '********'))

client = ClientV2(*creds)

calls = client.get_calls()  # .get_calls(call_id='fooobar', from='+123', to='+1213')
# [Call c-rtho4pobjpqudfvcgi24e7i, ..., Call c-gifkcvacopsvn5upq2vskqa]

print(calls)

call = calls[0]
# Call c-rtho4pobjpqudfvcgi24e7i

print(call.get_recordings())  # {}
print(call.send_dtmf(1))  # {}

call.update()

new_call = client.create_call('+14089155654', '+14088833839')  # Call type only @call-id and @from @to fields
# Call c-rtho4pobjpqudfvcgi24e7i


from client import Client as ClientV1

client = ClientV1(*creds)

calls = client.get_calls()
# [
# {'activeTime': '2014-09-05T09:44:20Z',
#  'callbackUrl': 'https://api.ct.bandwidth.com/tracking_events/v1/',
#  'chargeableDuration': 60,
#  'direction': 'in',
#  'endTime': '2014-09-05T09:44:25Z',
#  'events': '/calls/c-gs6hwl5agoosb72rcjw4iba/events',
#  'from': '+19194597763',
#  'id': 'c-gs6hwl5agoosb72rcjw4iba',
#  'recordingEnabled': False,
#  'recordings': '/calls/c-gs6hwl5agoosb72rcjw4iba/recordings',
#  'startTime': '2014-09-05T09:44:20Z',
#  'state': 'completed',
#  'to': '+19192755402',
#  'transcriptionEnabled': False,
#  'transcriptions': '/calls/c-gs6hwl5agoosb72rcjw4iba/transcriptions'},
# {'activeTime': '2014-09-05T09:44:20Z',
#  'callbackUrl': 'http://ec2-54-164-86-242.compute-1.amazonaws.com:8080/calls/out',
#  'chargeableDuration': 60,
#  'direction': 'out',
#  'endTime': '2014-09-05T09:44:25Z',
#  'events': '/calls/c-rveds623gx75nnteaykyira/events',
#  'from': '+19194597763',
#  'id': 'c-rveds623gx75nnteaykyira',
#  'recordingEnabled': False,
#  'recordings': '/calls/c-rveds623gx75nnteaykyira/recordings',
#  'startTime': '2014-09-05T09:44:20Z',
#  'state': 'completed',
#  'to': '+19192755402',
#  'transcriptionEnabled': False,
#  'transcriptions': '/calls/c-rveds623gx75nnteaykyira/transcriptions'}
# ]

the_call = calls[3]
call_id = the_call['id']
recordings = client.get_recordings(call_id)
# []

client.send_dtmf(call_id, '#')

client.get_call_info(call_id)

new_call_id = client.create_call('+14089155654', '+14088833839')