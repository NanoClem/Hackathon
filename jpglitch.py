#!/usr/bin/env python3
import os
import io
import copy
import random
import click
import xlrd

from itertools import tee
from PIL import Image




def pairwise(iterable):
    """Awesome function from the itertools cookbook
    https://docs.python.org/2/library/itertools.html
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)




# Collecting data from USA presidential results of 2016
# from an excel file

def USA_result(xls) :

    book  = xlrd.open_workbook("president_results_2016.xls")
    sheet = book.sheet_by_index(0)

    col             = 0
    tab_etats       = [""]*sheet.nrows
    tab_electeurs   = [0]*sheet.nrows
    tab_Hilary      = [0.0]*sheet.nrows
    tab_Trump       = [0.0]*sheet.nrows


    for i in range(sheet.nrows):

        Etats               = sheet.cell(rowx = i, colx = col).value
        tab_etats[i]        = Etats

        nb_electeurs        = sheet.cell(rowx = i, colx = col+1).value
        tab_electeurs[i]    = int(nb_electeurs)

        vote_Hilary         = sheet.cell(rowx = i, colx = col+2).value
        tab_Hilary[i]       = float(vote_Hilary)

        vote_Trump          = sheet.cell(rowx = i, colx = col+3).value
        tab_Trump[i]        = float(vote_Trump)


    all_results         = [tab_etats, tab_electeurs, tab_Trump, tab_Hilary]
    # print(tab_etats[0])
    # print(tab_electeurs[0])

    return all_results





# On construit une nouvelle image Jpeg en lui insérant les paramètres issus des données récupérées du fichier excel
# new_amount :
# new_seed :
# new_iterations : nombre de grands électeurs par Etats

class Jpeg(object):


    def __init__(self, image_bytes, new_amount, new_seed, new_iterations):

        self.bytes = image_bytes
        self.new_bytes = None

        self.amount = new_amount
        self.seed = new_seed
        self.iterations = new_iterations

        try:
            self.header_length = self.get_header_length()
        except ValueError as e:
            raise click.BadParameter(message=e.message)

        self.glitch_bytes()



    """Get the length of the header by searching sequential 0xFF 0xDA
    values. These values mark the end of a Jpeg header. We add two to give
    us a little leeway. We don't want to mess with the header.
    """

    def get_header_length(self):

        for i, pair in enumerate(pairwise(self.bytes)):
            if pair[0] == 255 and pair[1] == 218:
                result = i + 2
                return result

        raise ValueError('Not a valid jpg!')




    def glitch_bytes(self):
        """Glitch the image bytes, after the header based on the parameters.
        'Amount' is the hex value that will be written into the file. 'Seed'
        tweaks the index where the value will be inserted, rather than just a
        simple division by iterations. 'Iterations' should be self explanatory
        """

        amount = self.amount / 100
        seed = self.seed / 100
        iterations = self.iterations

        # work with a copy of the original bytes. We might need the original
        # bytes around if we glitch it so much we break the file.
        new_bytes = copy.copy(self.bytes)

        for i in (range(iterations)):
            max_index = len(self.bytes) - self.header_length - 4

            # The following operations determine where we'll overwrite a value
            # Illustrate by example

            # 36 = (600 / 50) * 3
            px_min = int((max_index / iterations) * i)

            # 48 = (600 / 50) * 3 + 1
            px_max = int((max_index / iterations) * (i + 1))

            # 12 = 48 - 36
            delta = (px_max - px_min)  # * 0.8

            # 36 + (12 * 0.8)
            px_i = int(px_min + (delta * seed))

            # If the index to be changed is beyond bytearray length file set
            # it to the max index
            if (px_i > max_index):
                px_i = max_index

            byte_index = self.header_length + px_i
            new_bytes[byte_index] = int(amount * 256)

        self.new_bytes = new_bytes



    def save_image(self, name):
        """Save the image to a file. Keep trying by re-glitching the image with
        less iterations if it fails
        """

        while True:
            try:
                stream = io.BytesIO(self.new_bytes)
                im = Image.open(stream)
                im.save("pictures/trump/" + name)
                return
            except IOError:
                if self.iterations == 1:
                    raise ValueError(message='This image is beyond\
                            repair, maybe try again?')

                self.iterations -= 1
                self.glitch_bytes()




#@click.command()
# @click.option('--amount', '-a', type=click.IntRange(0, 99, clamp=True),
#               default=random.randint(0, 99), help="Insert high or low values?")
# @click.option('--seed', '-s', type=click.IntRange(0, 99, clamp=True),
#               default=random.randint(0, 99), help="Begin glitching at the\
#                       start on a bit later on.")
# @click.option('--iterations', '-i', type=click.IntRange(0, 115, clamp=True),
#               default=random.randint(0, 115), help="How many values should\
#                       get replaced.")
# @click.option('--jpg', is_flag=True, help="Output to jpg instead of png.\
#                       Note that png is more stable")
# @click.option('--output', '-o', help="What to call your glitched file.")
# @click.argument('image', type=click.File('rb'))




def cli(data, states, electors, Trump_res, Hilary_res) :

    image_bytes = bytearray(data.read())

    for i in range(len(states)) :
        jpeg = Jpeg(image_bytes, Trump_res[i], Hilary_res[i], electors[i])

    # click.echo("\nScrambling your image with the following parameters:")
    # for key, value in jpeg.parameters.items():
    #     click.echo(message=key + ': ' + str(value))

        # if output:
        #     # TODO
        #     # make the extension here count as guide for what to save the file as
        #     # for now just ignore it if it's given
        #     name = output.rsplit('.')[0]
        # else:
        #     #state_name = states[i]
        #     name = image.name.rsplit('.')[0] + "_glitched"
        #
        # name += '%s' % ('.jpg' if jpg else '.png')
        state_name = states[i]
        jpeg.save_image(state_name + "_trump.png")

        # output = "\n Succes! Checkout" % name
        # click.echo(output)




if __name__ == '__main__':

    # Put here your excel file, make sure you gave the file's full path
    xls = "president_results_2016.xls"
    elections = USA_result(xls)
    #print("states")

    my_picture = open("trump.jpg", "rb")
    # my_picture.show()
    cli(my_picture, elections[0], elections[1], elections[2], elections[3])
