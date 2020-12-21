import os
import numpy as np
import matrix
import density
import gravity
import nuclear
import data

def evolution():
    '''A star is initialised in the form of proton number, neutron
    number, and mass number matrices. Every iteration utilises weighted
    probabilities in randomising the movement of elements under gravity,
    as well as in determining the nuclear fusion reactions that occur.
    The matrix dimensions may be modified under the variable 'dim'.
    '''

    # ignores runtime warning for handled ZeroDivisionError
    np.seterr(divide='ignore')

    # square matrix dimensions; minimum = 10
    dim = 20

    # proton number, neutron number, mass number matrices
    z, n, a = matrix.generate(dim)
    # energy matrix
    en = np.zeros((len(a), len(a)))
    # data handling arrays
    elm = np.array([1, 2, 6, 7, 8])
    stack = np.zeros(len(elm))
    # fusion rate array
    rate = [0]
    # total atomic mass
    print('\nMass: %d' %a.sum())

    # output images directory
    if not os.path.exists('images'):
        os.mkdir('images')

    # initial system
    pos = matrix.positions(a)
    cm = matrix.centre_of_mass(a, pos)
    dens = density.matrix(a)
    density.plot(dens, 'initial')

    # data handling
    comp = data.composition(z, pos)
    for i in range(len(stack)):
        for j in range(len(comp)):
            if elm[i] == comp[j, 0]:
                stack[i] = comp[j, 1]
                break
        else:
            stack[i] = 0
    elm = np.vstack((elm, stack))
    data.log(comp, 'w', 0)

    # control variables
    flag1 = True
    flag2 = False
    iter = 0
    print('\nIterations:\n')
    while flag1:
        iter += 1
        print(iter, end='. ')

        # gravitation
        pos = matrix.positions(a)
        grav = gravity.force(a, pos)
        grav *= 1 - 0.99*en.sum()
        for i in range(len(grav)):
            r = np.random.rand(1)
            j, k = pos[i]

            if r <= abs(grav[i, 0]):
                dir = int(grav[i, 0]/abs(grav[i, 0]))
                if a[j+dir, k] < a[j, k]:
                    z[j, k], z[j+dir, k] = z[j+dir, k], z[j, k]
                    n[j, k], n[j+dir, k] = n[j+dir, k], n[j, k]
            elif r <= np.abs(grav[i]).sum():
                dir = int(grav[i, 1]/abs(grav[i, 1]))
                if a[j, k+dir] < a[j, k]:
                    z[j, k], z[j, k+dir] = z[j, k+dir], z[j, k]
                    n[j, k], n[j, k+dir] = n[j, k+dir], n[j, k]
            a = z + n

        # nuclear fusion
        ctr = 0
        pos = matrix.positions(a)
        cm = matrix.centre_of_mass(a, pos)
        c_pos, c_temp = matrix.core(a, pos, cm)
        if not flag2:
            if c_temp > 7:
                flag2 = True
        else:
            for i in c_pos:
                j = i.copy()
                r = np.random.randint(2, size=2)
                # r[0] determines the axis (horizontal: 0, vertical: 1)
                # r[1] determines the direction along the axis
                dir = (-1)**r[1]
                if r[0]:
                    j[0] += dir
                else:
                    j[1] += dir
                p1 = [z[i[0], i[1]], n[i[0], i[1]]]
                p2 = [z[j[0], j[1]], n[j[0], j[1]]]
                try:
                    f = c_temp/(p1[0]*p2[0])
                    if f > 1:
                        f = 1
                except ZeroDivisionError:
                    f = 1
                e = en[i[0], i[1]]
                nr = nuclear.reaction(p1, p2, f, e)
                z[i[0], i[1]] = nr[0]
                n[i[0], i[1]] = nr[1]
                z[j[0], j[1]] = nr[2]
                n[j[0], j[1]] = nr[3]
                a = z + n
                en[i[0], i[1]] = nr[4]

                if [p1, p2] != [[nr[0], nr[1]], [nr[2], nr[3]]]:
                    ctr += 1
        rate.append(ctr)

        # data handling
        comp = data.composition(z, pos)
        for i in range(len(stack)):
            for j in range(len(comp)):
                if elm[0, i] == comp[j, 0]:
                    stack[i] = comp[j, 1]
                    break
            else:
                stack[i] = 0
        elm = np.vstack((elm, stack))
        data.log(comp, 'a', iter)

        # iterates till H + He (stellar fuel) drops below 5.00%
        fuel = stack[0] + stack[1]
        print('Fuel: %.2f%%\n' %fuel)
        if fuel < 5:
            flag1 = False

    # final system
    pos = matrix.positions(a)
    cm = matrix.centre_of_mass(a, pos)
    dens = density.matrix(a)
    density.plot(dens, 'final')
    density.profile(dens, cm)
    data.plot(elm[1:], iter+1)
    nuclear.plot_rate(rate, iter+1)

if __name__ == '__main__':
    evolution()
© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
