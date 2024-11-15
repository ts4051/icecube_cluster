'''
Organise information in tables with nice visualisation functions

Tom Stuttard
'''

# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# from __future__ import unicode_literals

# from builtins import range
# from builtins import str
# from future import standard_library
# standard_library.install_aliases()
# from builtins import object

class Table(object) :
    '''
    A class for dumping information as a table

    Use as:
        ```
        table = Table(["Run","Subrun"])
        table.addRow([1,1])
        table.addRow([1,2])
        print(table)
        ```
    '''

    #TODO Integrate with RelationalDict so can dump RelationalDict in this format


    def __init__(self,headers,colwidth=12) :
        self.divider = "|"
        self.spacer = "-"
        self.headers = headers
        self.colwidth = colwidth
        self.cellFormat = '%%-%is' % self.colwidth
        self.rows = []

    def addRow(self,row) :
        if len(row) != len(self.headers) :
            raise Exception( "Cannot add row to table, num columns %i does not match num headers %i" % (len(row),len(self.headers)) )
        else :
            self.rows.append(row)

    def addSpacerRow(self) :
        self.addRow( len(self.headers) * [self.formatSpacerCell()] )

    def formatSpacerCell(self) :
        return "".join( [ self.spacer for i in range(0,self.colwidth) ] )

    def formatSpacerRow(self) :
        return self.formatRow( len(self.headers) * [self.formatSpacerCell()] )

    def formatRow(self,row) :
        return self.divider + self.divider.join( [ self.cellFormat % str(h) for h in row ] ) + self.divider + "\n"

    @property
    def ncol(self) :
        return len(self.headers)

    @property
    def nrow(self) :
        return len(self.rows)

    def __len__(self) :
        return self.nrow

    def __str__(self) :
        tableString = self.formatSpacerRow()
        tableString += self.formatRow(self.headers) #Header
        tableString += self.formatSpacerRow()
        for row in self.rows :
            tableString += self.formatRow(row)
            #print '%-12i%-12i' % (10 ** i, 20 ** i)
        tableString += self.formatSpacerRow()
        return tableString

    def plot(self,ax=None,number_rows=True,**kw) :
        '''
        Plot the table with matplotlib
        '''

        import matplotlib.pyplot as plt
        from utils.plotting.figure import create_fig_for_ax, Figure

        kw.setdefault("loc","center")

        n_cols = len(self.headers)
        n_rows = len(self.rows)

        if ax is None :
            fig = Figure(nx=1,ny=1,figsize=(n_rows+1,n_cols+(1 if number_rows else 0)))
            ax = fig.get_ax()

        columns = self.headers
        cell_data = [ row for row in self.rows ]
        rows = list(range(n_rows)) if number_rows else None

        the_table = ax.table(   cellText=cell_data,
                                #colWidths=self.colwidth,
                                rowLabels=rows,
                                colLabels=columns,
                                **kw)

        ax.axis("tight")
        ax.axis("off")

        if ax is None :
            fig.fig.canvas.draw()
            fig.tight_layout()

        return the_table

    def tex(self) :
        '''
        Dump a tex version of the table
        '''

        #TODO this is hacky, improve it and document

        tex_str = r"\begin{tabular}{"
        # tex_str += r"\hline"
        tex_str += "|"
        for i in range(self.ncol) :
            tex_str += "c|"
        tex_str += "}\n"

        tex_str += "  " + " & ".join(self.headers) + r"\\ \hline \hline"
        tex_str += "\n"

        for i, row in enumerate(self.rows) :
            # print(row)
            row_str = [ str(x).replace(r"\_", r"_").replace(r"_", r"\_").replace("%", r"\%") for x in row ] # Fix underscores #TODO what else? should user handle this? #TODO UNder fixing screws entires that are already tex formatted
            tex_str += "  " + " & ".join(row_str) + r"\\ \hline" + "\n"

        tex_str += r"\end{tabular}"
        tex_str += "\n"

        return tex_str
        