import sys

skip = 1

if len(sys.argv) > 1:
    name = sys.argv[1]
    if len(sys.argv) > 2:
        skip = int(sys.argv[2])
else: 
    name = "dlv_log"

steps = {}
values = {}
val2 = {}
val4 = {}
temps = {}
pmax = 0
pmin = 9999999
tmax = 0
tmin = 9999999

total = 0
errs = 0
with open(name) as f:
    for l in f:
        if skip > 0:
            skip -= 1
            continue
        l=l.split()
        try:
            diff = int(l[2])
        except:
            errs += 1
            continue
        total += 1
        if diff in steps:
            steps[diff] += 1
        else:
            steps.update({diff: 1})

        val = int(l[1])
        pmax = max(pmax, val)
        pmin = min(pmin, val)

        if val in values:
            values[val] += 1
        else:
            values.update({val: 1})

        val = int(l[1]) // 2
        if val in val2:
            val2[val] += 1
        else:
            val2.update({val: 1})

        val = int(l[1]) // 4
        if val in val4:
            val4[val] += 1
        else:
            val4.update({val: 1})

        val = int(l[3])
        tmax = max(tmax, val)
        tmin = min(tmin, val)
        if val in temps:
            temps[val] += 1
        else:
            temps.update({val: 1})

print("\nNumber of evaluated samples:", total, ", reported errors:", errs )

sum = 0
print("\nDistribution of steps\n")
for k in sorted(steps):
    print ("{:>4} {:<}".format(k, steps[k]))
    sum += k * steps[k]

print("\nCumulated sum", sum)

print("\nTotal range of values: ", pmax, "-", pmin, "=", pmax - pmin + 1)
print ("\nMissing 14 bit pressure codes:", pmax - pmin + 1 - len(values))
print ("Missing 13 bit pressure codes:", (pmax // 2) - (pmin // 2) + 1 - len(val2))
print ("Missing 12 bit pressure codes:", (pmax // 4) - (pmin // 4) + 1 - len(val4))
print("\nMissing 11 bit temperature codes:", tmax - tmin + 1 - len(temps))
