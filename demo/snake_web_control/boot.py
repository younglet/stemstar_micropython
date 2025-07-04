# This file is executed on every boot (including wake-boot from deepsleep)


from connect_wifi import connect_wifi

connect_wifi(hostname='snake')

