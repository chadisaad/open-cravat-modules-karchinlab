import math

def stouffer(pvals):
    """
    Imitates scipy.stats.combine_pvalues(pvals, methof='stouffer')
    """
    Zi = [-inv_phi(p) for p in pvals]
    Z = sum(Zi)/math.sqrt(len(Zi))
    pval = 1-phi(Z)
    return Z, pval

def phi(x):
    """
    Cumulative normal function
    Described at: en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function
    Source: https://docs.python.org/3/library/math.html#special-functions
    """
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def inv_phi(p): 
    """
    Inverse cumulative normal function.
    Also called: Normal quantile function, probit function
    Described at: en.wikipedia.org/wiki/Normal_distribution#Quantile_function
    Also at: en.wikipedia.org/wiki/Probit#Computation
    Source: https://en.wikipedia.org/wiki/Normal_distribution#Quantile_function
    Relies on erfinv, which is the inverse error function
    """
    return (math.sqrt(2.0)*erfinv(2*p-1))

def erfinv(z):
    """
    Inverse error function
    Required because the scipy.special.erfinv relies on compiled functions
    Description: en.wikipedia.org/wiki/Error_function#Inverse_functions
    Source: stackoverflow.com/questions/42381244/pure-python-inverse-error-function
    Includes the three methods: inv_erf, polevl, p1evl
    """
    if z < -1 or z > 1:
        raise ValueError("`z` must be between -1 and 1 inclusive")

    if z == 0:
        return 0
    if z == 1:
        return float('inf')
    if z == -1:
        return -float('inf')

    # From scipy special/cephes/ndrti.c
    def ndtri(y):
        # approximation for 0 <= abs(z - 0.5) <= 3/8
        P0 = [
            -5.99633501014107895267E1,
            9.80010754185999661536E1,
            -5.66762857469070293439E1,
            1.39312609387279679503E1,
            -1.23916583867381258016E0,
        ]

        Q0 = [
            1.95448858338141759834E0,
            4.67627912898881538453E0,
            8.63602421390890590575E1,
            -2.25462687854119370527E2,
            2.00260212380060660359E2,
            -8.20372256168333339912E1,
            1.59056225126211695515E1,
            -1.18331621121330003142E0,
        ]

        # Approximation for interval z = sqrt(-2 log y ) between 2 and 8
        # i.e., y between exp(-2) = .135 and exp(-32) = 1.27e-14.
        P1 = [
            4.05544892305962419923E0,
            3.15251094599893866154E1,
            5.71628192246421288162E1,
            4.40805073893200834700E1,
            1.46849561928858024014E1,
            2.18663306850790267539E0,
            -1.40256079171354495875E-1,
            -3.50424626827848203418E-2,
            -8.57456785154685413611E-4,
        ]

        Q1 = [
            1.57799883256466749731E1,
            4.53907635128879210584E1,
            4.13172038254672030440E1,
            1.50425385692907503408E1,
            2.50464946208309415979E0,
            -1.42182922854787788574E-1,
            -3.80806407691578277194E-2,
            -9.33259480895457427372E-4,
        ]

        # Approximation for interval z = sqrt(-2 log y ) between 8 and 64
        # i.e., y between exp(-32) = 1.27e-14 and exp(-2048) = 3.67e-890.
        P2 = [
            3.23774891776946035970E0,
            6.91522889068984211695E0,
            3.93881025292474443415E0,
            1.33303460815807542389E0,
            2.01485389549179081538E-1,
            1.23716634817820021358E-2,
            3.01581553508235416007E-4,
            2.65806974686737550832E-6,
            6.23974539184983293730E-9,
        ]

        Q2 = [
            6.02427039364742014255E0,
            3.67983563856160859403E0,
            1.37702099489081330271E0,
            2.16236993594496635890E-1,
            1.34204006088543189037E-2,
            3.28014464682127739104E-4,
            2.89247864745380683936E-6,
            6.79019408009981274425E-9,
        ]

        s2pi = 2.50662827463100050242
        code = 1

        if y > (1.0 - 0.13533528323661269189):      # 0.135... = exp(-2)
            y = 1.0 - y
            code = 0

        if y > 0.13533528323661269189:
            y = y - 0.5
            y2 = y * y
            x = y + y * (y2 * polevl(y2, P0, 4) / p1evl(y2, Q0, 8))
            x = x * s2pi
            return x

        x = math.sqrt(-2.0 * math.log(y))
        x0 = x - math.log(x) / x

        z = 1.0 / x
        if x < 8.0:                 # y > exp(-32) = 1.2664165549e-14
            x1 = z * polevl(z, P1, 8) / p1evl(z, Q1, 8)
        else:
            x1 = z * polevl(z, P2, 8) / p1evl(z, Q2, 8)

        x = x0 - x1
        if code != 0:
            x = -x

        return x

    result = ndtri((z + 1) / 2.0) / math.sqrt(2)

    return result

def polevl(x, coefs, N):
    ans = 0
    power = len(coefs) - 1
    for coef in coefs:
        ans += coef * x**power
        power -= 1
    return ans

    return ans

def p1evl(x, coefs, N):
    return polevl(x, [1] + coefs, N)