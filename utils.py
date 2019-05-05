# -*- coding: utf-8 -*-

import socket


def is_valid_address(address):
    """
    验证ipv4 or ipv6
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except socket.error:  # not a valid address
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
    return True