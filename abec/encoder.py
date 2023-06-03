def decoder(ind, parameters):
    '''
    Decoder function for continous problems
    From binary to decimal
    '''
    sum = 0
    j = 0
    l = int(parameters["INDSIZE"]/parameters["NDIM"])
    result = []
    precision = (parameters["MAX_POS"]-parameters["MIN_POS"])/(2**(l)-1)
    for d in range(1, parameters["NDIM"]+1):
        for i, bin in enumerate(ind["pos"][j:d*l], 0):
            sum += bin*(2**(l-i-1))
        decode = sum*precision + parameters["MIN_POS"]
        result.append(decode)
        j = d*l

        sum = 0

    ind["pos"] = result
    return ind

def encoder(ind, parameters):
    '''
    Encoder function for continous problems
    From decimal to binary
    '''
    l = int(parameters["INDSIZE"]/parameters["NDIM"])
    result = ""
    for d in ind["pos"]:
        encode = ((2**(l)-1)*(d - parameters["MIN_POS"]))/(parameters["MAX_POS"]-parameters["MIN_POS"])
        result += "{0:016b}".format(int(encode))
    result = list(result)

    print (result)

    for i, b in enumerate(result):
        result[i] = int(b)

    ind["pos"] = result
    return ind
