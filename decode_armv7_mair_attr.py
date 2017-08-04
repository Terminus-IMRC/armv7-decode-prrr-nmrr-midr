#!/usr/bin/env python3

import sys

def decode_armv7_mair_attr(val):
    val &= 0b11111111

    if (val >> 4) == 0b0000:
        val_3_0 = val & 0b1111
        if val_3_0 == 0b0000:
            type = 'ordered'
        elif val_3_0 == 0b0100:
            type = 'device'
        else:
            type = 'unpredictable'
        print('0x%02x, %s,,,,,,' % (val, type))
    else:
        type = 'normal'

        def decode_inner_or_outer(val):
            may_be_unpredictable = False
            val &= 0b1111
            val_3_2 = val >> 2
            val_1_0 = val & 0b11
            if val_3_2 == 0b00:
                may_be_unpredictable = True
                method = 'write-through'
            elif val_3_2 == 0b01:
                if val_1_0 != 0b00:
                    method = 'non-cacheable'
                else:
                    may_be_unpredictable = True
                    method = 'write-back'
            elif val_3_2 == 0b10:
                method = 'write-through'
            elif val_3_2 == 0b11:
                method = 'write-back'

            if val_1_0 == 0b11:
                alloc_policy = 'Read and Write'
            elif val_1_0 == 0b10:
                alloc_policy = 'Read'
            elif val_1_0 == 0b01:
                alloc_policy = 'Write'
            elif val_1_0 == 0b00:
                alloc_policy = 'None'

            return (method, may_be_unpredictable, alloc_policy)

        outer_method, outer_may_be_unpred, outer_alloc_policy = \
                                            decode_inner_or_outer(val >> 4)
        inner_method, inner_may_be_unpred, inner_alloc_policy = \
                                            decode_inner_or_outer(val & 0b1111)

        print('0x%02x, %s, %s, %s, %s, %s, %s, %s' % (val, type,
                                        outer_method, outer_alloc_policy,
                                        'Yes' if outer_may_be_unpred else 'No',
                                        inner_method, inner_alloc_policy,
                                        'Yes' if inner_may_be_unpred else 'No'))

def main():
    if len(sys.argv) <= 1:
        return
    print('Attr, Value, Type, Outer Method, Outer Alloc Policy, Outer Unpred, Inner Method, Inner Alloc Policy, Inner Unpred')
    count = 0
    for s in sys.argv[1:]:
        val = int(s, 0)
        for i in range(4):
            print('%d, ' % count, end = '')
            decode_armv7_mair_attr(val)
            val >>= 8
            count += 1

if __name__ == '__main__':
    main()
