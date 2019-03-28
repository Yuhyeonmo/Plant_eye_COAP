from firebase import firebase

fire = firebase.FirebaseApplication('https://fognode-71631.firebaseio.com/', )
result = fire.get('/control_HW/ONOFF', None)
if result == 'OFF':
    print(result)