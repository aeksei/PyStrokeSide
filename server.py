import eventlet
import socketio
from eventlet import wsgi

sio = socketio.Server()


async def run():
    app = socketio.WSGIApp(sio)
    await wsgi.server(eventlet.listen(('', 5000)), app)


@sio.event
def connect(sid, environ):
    print('connect ', sid)


@sio.event
def my_message(sid, data):
    print('message ', data)
    sio.emit('message', {'data': 'foobar'})


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)

    while True:
        sio.emit('message', {'data': 'foobar'})
        sio.sleep(2)
