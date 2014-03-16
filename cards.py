#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A program to translate a short string into the order of a pack of cards and vice versa
#
# There are 52! ways to arrange a standard pack of playing cards, so that we can
# transmit log(52!)/log(2) = 225 bits of data using a pack of cards
#
# This program uses an alphabet of 67 characters (6.07 bits per character)
# so that we can send a 53 character message using the pack.
# 
# The alphabet could be reduced (e.g. leaving out capitals) to increase the
# capacity for English, though for TinyURLs and the like, perhaps the ability
# to transmit upper and lower case is useful.
# 
# (c) 2014 Richard George

import sys;

# Converting integers to playing cards

deck = {};
face = {0:'A', 1:'2', 2:'3', 3:'4', 4:'5', 5:'6', 6:'7',
        7:'8', 8:'9', 9:'10', 10:'J', 11:'Q', 12:'K'};

suit1 = {0:u'\u2663', 1:u'\u2662', 2:u'\u2661', 3:u'\u2660'};
suit2 = {0:'C', 1:'D', 2:'H', 3:'S'};
suit3 = {0:u'\u2664', 1:u'\u2665', 2:u'\u2666', 3:u'\u2667'};

# Converting playing cards to integers

lookup = {};

encode_card = { 0: lambda n: face[n % 13] + suit1[n // 13], \
                1: lambda n: face[n % 13] + suit2[n // 13], \
                2: lambda n: face[n % 13] + suit3[n // 13], \
                3: lambda n: suit1[n // 13] + face[n % 13], \
                4: lambda n: suit2[n // 13] + face[n % 13], \
                5: lambda n: suit3[n // 13] + face[n % 13], \
                6: lambda n: suit2[n // 13].lower() + face[n % 13], \
                7: lambda n: face[n % 13] + suit2[n // 13].lower()}; 

# make a lookup table to turn strings into their ordinal values

for i in range(0,52):
    for j in range(0,8):
        lookup[encode_card[j](i)]=i;

# put a leading space in front of short cards, e.g. ' 2D' '10D'
card = lambda n: encode_card[0](n) if n % 13 == 9 else ' '+encode_card[0](n);

# Convert a message into an integer, and vice versa

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,<>£$#\"! ";
encode = {};
decode = {};

for i,v in enumerate(alphabet):
    encode[v]=i;
    decode[i]=v;
    
# Real code starts here

def check_number_range(n):
    '''Verify that a number is in the range that can be represented by a pack of playing cards'''
    
    m = 1;
    for i in range(1,52):
        m *= i;
    m -= 1;
    
    if n>m:
        raise Exception('Maximum number exceeded for playing card encoding');
    else:
        return True;
        
def pack_for_number(n=0):
    '''Convert an integer n into a list of the numbers 0...52 permuted in an order that represents the number'''
    
    check_number_range(n);
     
    # Set up the insertions map
    insertions = {};
    deck = {};
    
    for i in range(0,52):
        insertions[i] = i;
        deck[i] = -1;
  
    # The pack is represented in a varying number basis  
    for i in range(51,-1,-1):
        # Place card 51-i at logical position insert_pos
        insert_pos = n % (i+1);

        deck[insertions[insert_pos]] = 51-i;
        
        # We can't insert a second card on top of the one just inserted
        # Track this
        new_insertions={};
        del insertions[insert_pos];
        for j,v in enumerate(insertions.keys()):
            new_insertions[j]=insertions[v];        
        insertions = new_insertions;

        # Reduce the number by throwing away the least significant digit        
        n = n // (i+1);
    
    return validate_pack(deck.values());
            
def validate_pack(p):
    '''Check that the list p could represent a pack of playing cards'''
    
    if len(p)!=52:
        raise Exception('Incorrect number of cards in the pack, must be 52');
        
    # Each card should appear once and only once in the pack
    seen = {};
    for i in range(0,52):
        seen[i]=0;
        
    for i in p:
        seen[i]+=1;
        
    for i in range(0,52):
        if seen[i]!=1:
            raise Exception('Saw the #%d card %d times, should be once only' % (i,seen[i]));
    
    return p;
    
def number_for_pack(p):
    '''Convert a permuted list of the integers 0...52 into a single integer, representing the permutation'''
    
    # Set up some logic
    seen_pos = {};
    card_pos = {};
    logical = {};
    
    for i,v in enumerate(p):
        card_pos[v] = i;
        
    for i in range(0,52):
        logical[i] = i;
        
    # Fill the array values with the logical value of the n'th card
    value = {};
    # Iterate over each card, and find it's logical value
    for card in range(0,52):
        physical = card_pos[card];
        # print "Card #%d is at physical position %d, with logical value %d" % (card,physical,logical[physical]);
        value[card] = logical[physical];
        seen_pos[card_pos[card]]=1;
        
        new_logical={};
        v=0;
        for j in range(0,52):
            if seen_pos.has_key(j):
                continue;
            new_logical[j]=v;
            v+=1;
        logical=new_logical;
        
    # Convert the dictionary of logical values into a single integer
    result = 0;
    for i in range(51,-1,-1):
        if value[i] == -1:
            return -1;
        result *= (52-i);
        result += value[i];
    
    return result;
    
def print_pack(p):
    '''Print the pack of cards as a 4x13 grid'''
    pack={};
    for i,v in enumerate(p):
        pack[i]=v;
        
    for c in range(0,13):
        line = '    ';
        for r in range(0,4):
            i = (r*13)+c;
            line += '%2d: ' % (i+1) + card(pack[i]) + '    ';
        print line;

def pack_oneline(pack,uni=True):
    '''Return a string listing the pack of cards on one line'''
    
    result = '';
    for i in range(0,52):
        result += encode_card[0](pack[i]) if uni else encode_card[1](pack[i]);
        if i!=51:
            result += ' ';
    return result;
        
def encode_message_to_number(i):
    '''Convert a string drawn from alphabet into an integer'''

    m = i.strip();
    if len(m)==0:
        return 0;
    
    result = 0;
    for i in range(len(m)-1,-1,-1):
        result *= len(alphabet);
        result += encode[m[i]];
    return result+1;

def decode_number_to_message(n):
    '''Convert an integer into a string, using letters drawn from alphabet'''
    
    # Special case: n=0 represents an empty string
    if n==0:
        return '';
    
    # n wasn't zero, so decrement it, therefore we can represent the string 'A'
    n-=1;
        
    # Pull out the first letter of the string
    result = decode[n % len(alphabet)];
    n //= len(alphabet);
    
    # Pull out any remaining letters
    while n>0:
        result += decode[n % len(alphabet)];
    
        n //= len(alphabet);
    
    # voila
    return result;

def parse_pack_from_string(i):
    '''Parse a string representing a pack of playing cards into a list of the integers 0...52'''
    
    s = i.decode('utf-8');
    tokens=s.split();
    pack={};
    for i in range(0,52):
        pack[i] = lookup[tokens[i]];
    return pack.values();
    
def interactive(mode):
    '''Run the encoding/decoding via a simple command-line interface'''
    
    if mode=='enc':
        m = raw_input('Enter a message to encode: ');
        print "\nYour message is represented by the following pack of cards:\n";
        print pack_oneline(pack_for_number(encode_message_to_number(m)));
        print "\n(without unicode)\n";
        print pack_oneline(pack_for_number(encode_message_to_number(m)),uni=False);        
    elif mode=='dec':
        p = raw_input('Enter a pack to decode: ');
        print "\nThe message decodes as:\n";
        print decode_number_to_message(number_for_pack(parse_pack_from_string(p)));
    else:
        print "\nDidn't recognise action '%s'\n" % mode;
        
# Decode the command line arguments

if __name__ == "__main__": 
    if len(sys.argv)==4:
        if sys.argv[1]=='enc':
            with open(sys.argv[2],'r') as f1:
                with open(sys.argv[3],'w') as f2:
                    m = f1.readline().strip();
                    f2.write(pack_oneline(pack_for_number(encode_message_to_number(m))));
                    
        elif sys.argv[1]=='dec':
            with open(sys.argv[2],'r') as f1:
                with open(sys.argv[3],'w') as f2:
                    m = f1.readline().strip();
                    f2.write(decode_number_to_message(number_for_pack(parse_pack_from_string(m))));
            
    elif len(sys.argv)==2:
        interactive(sys.argv[1]);
                    
    else:
        mode = raw_input('Enter \'enc\' for encoding or \'dec\' for decoding: ');
        interactive(mode);
