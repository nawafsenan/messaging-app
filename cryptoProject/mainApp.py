# import RSA
# import math
# import random
#
#
# #public_B = None
# p, q = RSA.generate_prime(100,500), RSA.generate_prime(100, 500)
# while p == q:
#     q = RSA.generate_prime(100,500)
#
# n = p * q
# phi = (p - 1) * (q - 1)
# public =  random.randint(3, phi - 1)
# while math.gcd(public, phi)!= 1:
#     public = random.randint(3, phi - 1)
# private = RSA.mod_inverse1(public, phi)
#
# #test
# print(public)
# print(private)
# message = "zipy"
# message_encoded = [ord(ch) for ch in message]
#
# # ( m^e ) mod n
#
# cipher = [pow(ch, public, n) for ch in message_encoded ]
# print("cipher text : ",cipher)
#
# message_encoded = [pow(ch,private,n) for ch in cipher]
# message_final = "".join(chr(ch) for ch in message_encoded)
# print("plain text : ",message_final)