import hashlib
import ecc

def hash_160(public_key):
    try:
        md = hashlib.new('ripemd160')
        md.update(hashlib.sha256(public_key).digest())
        return md.digest()
    except Exception:
        import ripemd
        md = ripemd.new(hashlib.sha256(public_key).digest())
        return md.digest()

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
    long_value = 0L

    for (i, c) in enumerate(v[::-1]):
        long_value += (256**i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    nPad = 0
    for c in v:
        if c == '\0': nPad += 1
        else: break

    return (__b58chars[0]*nPad) + result

def b58decode(v):
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base**i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]: nPad += 1
        else: break

    result = chr(0)*nPad + result

    return result

def EncodeBase58Check(vchIn):
    hash = hashlib.sha256(hashlib.sha256(vchIn).digest()).digest()
    return b58encode(vchIn + hash[0:4])

def DecodeBase58Check(psz):
    vchRet = b58decode(psz)
    key = vchRet[0:-4]
    csum = vchRet[-4:]
    hash = hashlib.sha256(hashlib.sha256(key).digest()).digest()
    cs32 = hash[0:4]
    if cs32 != csum:
        return None
    else:
        return key

def pointToPubkey(point, compressed = True):
    x = ('%064x' % point[0]).decode('hex')
    if compressed:
        return ('%02x' % (2 + (point[1] & 1))).decode('hex') + x
    else:
        return chr(4) + x + ('%064x' % point[1]).decode('hex')

def EC_YfromX(x, odd = True):
    _p = ecc.cP
    _a = ecc.cA
    _b = ecc.cB
    Mx = x
    My2 = pow(Mx, 3, _p) + _a * pow(Mx, 2, _p) + _b % _p
    My = pow(My2, (_p+1)/4, _p )
    if odd == bool(My & 1):
        return My
    return _p - My

def pubkeyToPoint(pubkey):
    if pubkey[0] == chr(4):
        x = int(pubkey[1:33].encode('hex'),16)
        y = int(pubkey[33:65].encode('hex'),16)
        return (x,y)
    elif pubkey[0] == chr(2) or pubkey[0] == chr(3):
        x = int(pubkey[1:33].encode('hex'),16)
        y = EC_YfromX(x, int(pubkey[0].encode('hex'),16) & 1)
        return (x,y)
    else:
        raise Exception('pubkeyToPoint: Not a valid pubkey')

def pubkeyToAddress(pubkey):
    return EncodeBase58Check(chr(0) + hash_160(pubkey))

def privkeyToWIF(priv, compressed = True):
    if len(priv) != 32: raise Exception('privkeyToWIF: Not a valid privkey')
    v = chr(128) + priv
    if compressed: v += chr(1)
    return EncodeBase58Check(v)

def wifToPrivkey(WIF):
    decoded = DecodeBase58Check(WIF)
    if decoded == None: raise Exception('wifToPrivkey: invalid WIF privkey')
    if len(decoded) == 34: return decoded[1:-1]
    if len(decoded) == 33: return decoded[1:]
    raise Exception('wifToPrivkey: invalid WIF privkey')

def privkeyToPubkey(priv, compressed = True):
    secret = int(priv.encode('hex'),16)
    pub_point = ecc.EC_mult(secret)
    return pointToPubkey(pub_point, compressed)

