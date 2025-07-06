import random
import math
from selectors import SelectSelector


#from pydoc import plaintext


#import pickle as pickle
####################################################################################3
def is_prime(num):
    if num < 2:
        return False
    for i in range(3, math.floor(math.sqrt(num)),2):
        if num % i == 0:
            return False
    return True
#####################################################################################
def is_prime1 (number):
    if number < 2:
        return False
    for i in range (2, number // 2 +1):
        if number % i == 0:
            return False
    return True


def generate_prime(min,max):
    prime = random.randint(min,max)
    while not is_prime1(prime):
        prime = random.randint(min, max)

    return prime
######################################################3##############
def mod_inverse(a,b):    #e, phi
    mod = b
    y = 0
    x = 1
    if a > 1:
        k = a // b
        temp = b
        b = a % b
        a = temp
        temp = y

        y = x -k *y
        x = temp
    if x < 0:
        x = x+mod
    return x #mul inverse
#################################################################################

def mod_inverse1(a, b):
    for x in range (3, b):
        if (x * a) % b == 1:
            return x
    raise ValueError ("Mod_inverse does not exist!")





p, q = generate_prime(100,500), generate_prime(100, 500)
while p == q:
    q = generate_prime(100,500)

n = p * q
phi = (p - 1) * (q - 1)


# public key -->  e must be prime , less that phi, not a factor of phi
e = random.randint(3, phi - 1)
while math.gcd(e,phi)!= 1:
    e = random.randint(3, phi - 1)
# private key
d = mod_inverse1(e, phi)



#test

message = "samplkey"
message_encoded = [ord(ch) for ch in message]

# ( m^e ) mod n

cipher = [pow(ch, e, n) for ch in message_encoded ]
print("cipher text : ",cipher)

message_encoded = [pow(ch,d,n) for ch in cipher]
message = "".join(chr(ch) for ch in message_encoded)
print("plain text : ",message)








