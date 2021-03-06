import aiosqlite3
import os

async def get_data (queries):
    # hugo - aalen
    dbpath = os.path.join(os.path.dirname(__file__), 
                          'data',
                          'wgtopgenessummary.sqlite')
    conn = await aiosqlite3.connect(dbpath)
    cursor = await conn.cursor()
    q = 'select hugo, aalen from genelen'
    await cursor.execute(q)
    genelen = {}
    for row in await cursor.fetchall():
        genelen[row[0]] = row[1]
    
    dbpath = queries['dbpath']
    conn = await aiosqlite3.connect(dbpath)
    cursor = await conn.cursor()

    # 1 sample?
    q = 'select count(distinct(base__sample_id)) from sample'
    await cursor.execute(q)
    #num_total_sample = len(await cursor.fetchall())
    num_total_sample = (await cursor.fetchone())[0]
    if num_total_sample == 1:
        response = {'data': None}
        return response

    gene_var_perc = {}
    q = 'select variant.base__hugo, count(*) from variant, variant_filtered where variant.base__uid=variant_filtered.base__uid and variant.base__hugo is not null group by variant.base__hugo'
    await cursor.execute(q)
    for row in await cursor.fetchall():
        hugo = row[0]
        if hugo == '':
            continue
        count = row[1]
        aalen = genelen[hugo]
        perc = count / aalen
        gene_var_perc[hugo] = perc
    
    num_gene_to_extract = 10
    sorted_hugos = sorted(gene_var_perc, key=gene_var_perc.get, reverse=True)
    extracted_hugos = sorted_hugos[:num_gene_to_extract]

    genesampleperc = {}
    for hugo in extracted_hugos:
        q = 'select count(distinct(sample.base__sample_id)) from sample, variant where variant.base__uid=sample.base__uid and variant.base__hugo="' + hugo + '"'
        await cursor.execute(q)
        num_sample = (await cursor.fetchone())[0]
        perc_sample = num_sample / num_total_sample * 100.0
        genesampleperc[hugo] = perc_sample
    sorted_hugos = sorted(genesampleperc, key=genesampleperc.get, reverse=True)
    response = {'data': []}
    for hugo in sorted_hugos:
        response['data'].append([hugo, genesampleperc[hugo]])

    return response
