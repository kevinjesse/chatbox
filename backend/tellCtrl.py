#
# @author Kevin Jesse
# @email kevin.r.jesse@gmail.com
#

import random

import candidates
import database_connect
import movieCtrl
import numpy as np

cur = database_connect.db_connect()


def ctrl(cache_results, titles_user, scoreweights, history):

    temp = ''
    for k, v in cache_results.iteritems():
        temp += k.title() + " : "
        if v:
            temp += ','.join(v).title() + " | \n "
        else:
            temp += 'No Preference' + " | \n "
            # qtup = ("Here is the information I have gathered in this conversation. " + temp, 'tell')
            # mscores, mmap = candidates.find(cache_results[userid])
    mscores, mmap = candidates.find(titles_user, cache_results)
    movieWithScore = sorted(zip(mmap, np.dot(mscores, scoreweights)), key=lambda tup: tup[1],
                        reverse=True)

    print
    print(movieWithScore[:10])
    print
    # output = []
    # # not sure why this occasionally excepts keyerror from movieWith Score
    # if movieWithScore:
    #     data = movieCtrl.moviebyID(movieWithScore[0][0])
    #     print data
    #     # process directors and actors into readable for output
    #     output.append("How about " + data[1] + " (" + data[
    #         3] + ")? ")
    #     if len(data) > 10:
    #         dlist = data[12].split(' ')
    #         alist = data[14].split(' ')
    #         actorNameList = movieCtrl.actorsbyID(alist)
    #         directorNameList = movieCtrl.actorsbyID(dlist)
    #         output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
    #                       ", ".join(directorNameList) + ".")
    #     output.append("This film is {} minutes long. It is {} {} movie, and is rated {}.".format(
    #         data[8],
    #         "an" if any(v in data[4][:1].lower() for v in ['a','e','i','o','u']) else "a",
    #         data[4].replace(" ", ",", data[4].count(" ") - 1)\
    #                 .replace(" ", " and ")\
    #                 .replace(",", ", "),
    #         data[6]
    #     ))
    # return output
    return movieWithScore

# def tieBreaker(movieWithScore):
def sort_by_rating(movielist):
    alistval = ["('"+str(movielist[i])+"' ," + str(i+1) + ")" for i in range(0, len(movielist))]
    aliststr = """, """.join(alistval)
    sqlstring = """SELECT averagerating FROM ratings join (VALUES""" + aliststr + """) AS X (tconst, ordering) ON ratings.tconst = X.tconst ORDER BY X.ordering """
    #print "SQLString:", sqlstring
    cur.execute(sqlstring)
    rows = cur.fetchall()
    movieWithRating = sorted(zip(movielist, rows), key=lambda tup: tup[1],
                            reverse=True)
    print(movieWithRating[:10])
    return movieWithRating


def to_text(movieWithScore):
    output = []
    if movieWithScore:
        tie = [movie[0] for movie in movieWithScore if movieWithScore[0][1] == movie[1]]
        movieID = random.choice(tie)

        data = movieCtrl.moviebyID(movieID)
        print(data)
        # process directors and actors into readable for output
        output.append("How about " + data[1] + " (" + data[
            3] + ")? ")
        if len(data) > 10:
            dlist = data[12].split(' ')
            alist = data[14].split(' ')
            actorNameList = movieCtrl.actorsbyID(alist)
            directorNameList = movieCtrl.actorsbyID(dlist)
            output.append(data[1] + " stars " + ", ".join(actorNameList) + " and is directed by " + \
                          ", ".join(directorNameList) + ".")
        output.append("This film is {} minutes long. It is {} {} movie, and is rated {}.".format(
            data[8],
            "an" if any(v in data[4][:1].lower() for v in ['a','e','i','o','u']) else "a",
            data[4].replace(" ", ",", data[4].count(" ") - 1)\
                    .replace(" ", " and ")\
                    .replace(",", ", "),
            data[6]
        ))
    return output


# temp = ['tt0475290', 'tt2005151', 'tt0160127', 'tt0117665', 'tt0109254', 'tt0363589', 'tt0988045', 'tt0250258', 'tt0059113', 'tt0113627', 'tt0102975', 'tt0090555', 'tt1893256', 'tt0108399', 'tt1448755', 'tt3062096', 'tt0125664', 'tt0070608', 'tt0057115', 'tt0120660', 'tt0145487', 'tt1058017', 'tt0356150', 'tt0043456', 'tt0256380', 'tt0089530', 'tt0119528', 'tt0120663', 'tt0025316', 'tt0082010', 'tt2404435', 'tt0093428', 'tt0112508', 'tt0171363', 'tt0398712', 'tt0118615', 'tt0112818', 'tt0119488', 'tt1964418', 'tt0338564', 'tt0309593', 'tt0332452', 'tt0116683', 'tt0112579', 'tt0071230', 'tt1656190', 'tt0099371', 'tt0228786', 'tt0118928', 'tt0080453', 'tt0263488', 'tt0139654', 'tt0368933', 'tt0133240', 'tt0050212', 'tt0085794', 'tt0110932', 'tt1024648', 'tt2261287', 'tt0315327', 'tt0120363', 'tt0120667', 'tt5013056', 'tt0101507', 'tt0101700', 'tt0246460', 'tt0240890', 'tt0241303', 'tt0251160', 'tt0257106', 'tt0278504', 'tt0250494', 'tt0236493', 'tt0264464', 'tt0265086', 'tt0256009', 'tt0401792', 'tt1155076', 'tt0087538', 'tt0898367', 'tt0133751', 'tt0448134', 'tt0465494', 'tt0042876', 'tt0091474', 'tt0118971', 'tt0325980', 'tt0375063', 'tt1320261', 'tt0362270', 'tt0099938', 'tt0302640', 'tt0408839', 'tt0109707', 'tt0032138', 'tt0159365', 'tt0195685', 'tt0043274', 'tt0101889', 'tt0241527', 'tt0390384', 'tt0096446', 'tt0848228', 'tt0317248', 'tt0145660', 'tt0280707', 'tt1099212', 'tt0120586', 'tt0082971', 'tt0099052', 'tt0096874', 'tt0230011', 'tt0080487', 'tt0113568', 'tt0091203', 'tt1174732', 'tt0099088', 'tt0310793', 'tt0300051', 'tt0395169', 'tt1179056', 'tt0450345', 'tt0379217', 'tt2294629', 'tt1714206', 'tt0088763', 'tt0404390', 'tt0253556', 'tt0128853', 'tt0079945', 'tt0286499', 'tt0304141', 'tt0765010', 'tt0117913', 'tt0344510', 'tt0205000', 'tt0112401', 'tt0107362', 'tt0119229', 'tt0098536', 'tt0098635', 'tt0462499', 'tt0138704', 'tt1375666', 'tt0970416', 'tt0300556', 'tt0418819', 'tt0120912', 'tt0071807', 'tt0106697', 'tt0267626', 'tt0082406', 'tt0102057', 'tt0265208', 'tt0159273', 'tt0227538', 'tt0369702', 'tt0120148', 'tt0167260', 'tt0036613', 'tt0118688', 'tt0300471', 'tt0116209', 'tt0314353', 'tt0107977', 'tt0116778', 'tt0113855', 'tt0119396', 'tt0120828', 'tt0152930', 'tt0183505', 'tt0097814', 'tt0217869', 'tt0097815', 'tt0234215', 'tt0097937', 'tt0097958', 'tt0098439', 'tt0332280', 'tt0098084', 'tt1212450', 'tt1280558', 'tt0099348', 'tt1528071', 'tt0099423', 'tt1956620', 'tt0099674', 'tt0099685', 'tt0102510', 'tt0959337', 'tt0268126', 'tt0103064', 'tt0103074', 'tt0103644', 'tt0104815', 'tt0105665', 'tt0100802', 'tt0101393', 'tt0099653', 'tt0099810', 'tt0106856', 'tt0104691', 'tt0099871', 'tt0084602', 'tt0104694', 'tt0106677', 'tt0310775', 'tt0099785', 'tt0100935', 'tt0100403', 'tt0099700', 'tt0099365', 'tt0101921', 'tt0099422', 'tt0100157', 'tt0105236', 'tt0104952', 'tt0100814', 'tt0100405', 'tt0100502', 'tt0104652', 'tt0082096', 'tt0332379', 'tt0109686', 'tt0110148', 'tt0110413', 'tt0110475', 'tt0111161', 'tt0111495', 'tt0112864', 'tt0113247', 'tt0105698', 'tt0111282', 'tt0104348', 'tt0112281', 'tt0105323', 'tt0103772', 'tt0104714', 'tt0107290', 'tt0109813', 'tt0364970', 'tt0107144', 'tt0106489', 'tt0113540', 'tt0108037', 'tt0103919', 'tt0106965', 'tt0110912', 'tt0112642', 'tt0105417', 'tt0111257', 'tt0102059', 'tt0107688', 'tt0107206', 'tt0103776', 'tt0101862', 'tt0382625', 'tt0382932', 'tt0105812', 'tt0108160', 'tt0106918', 'tt0104231', 'tt0101540', 'tt0102266', 'tt0107211', 'tt0110074', 'tt0106220', 'tt0106582', 'tt0105793', 'tt0107207', 'tt0404030', 'tt0102685', 'tt0103241', 'tt0114746', 'tt0115433', 'tt0116136', 'tt0116282', 'tt0258000', 'tt0245712', 'tt0261392', 'tt0256415', 'tt0266697', 'tt0257360', 'tt0252866', 'tt0265459', 'tt0430105', 'tt0117008', 'tt0118583', 'tt0118689', 'tt0115759', 'tt0117802', 'tt0113071', 'tt0118884', 'tt0114694', 'tt0112384', 'tt0116040', 'tt0116705', 'tt0118749', 'tt0107822', 'tt0109445', 'tt1904996', 'tt0455538', 'tt0117705', 'tt0108358', 'tt0114069', 'tt0114814', 'tt0117571', 'tt0112431', 'tt0117509', 'tt0118799', 'tt0116908', 'tt0116922', 'tt0114898', 'tt0114558', 'tt0114388', 'tt0118887', 'tt0117666', 'tt0113481', 'tt0243017', 'tt0480025', 'tt0119395', 'tt0480249', 'tt0116629', 'tt0112697', 'tt0108550', 'tt0112573', 'tt0109831', 'tt0113161', 'tt0112462', 'tt0113497', 'tt0110478', 'tt0113118', 'tt0113101', 'tt0114148', 'tt0111070', 'tt0111301', 'tt0112442', 'tt0113189', 'tt0800069', 'tt0118880', 'tt0120694', 'tt0120735', 'tt0120737', 'tt0119654', 'tt0119282', 'tt0120102', 'tt0120382', 'tt0120179', 'tt0120631', 'tt0119094', 'tt0119190', 'tt0120184', 'tt0119177', 'tt0120347', 'tt0118929', 'tt0887912', 'tt0119173', 'tt0119698', 'tt0119137', 'tt0119303', 'tt0119051', 'tt0120685', 'tt0120591', 'tt0119643', 'tt0120647', 'tt0120201', 'tt0120744', 'tt0120679', 'tt0113957', 'tt0338526', 'tt1013753', 'tt1017460', 'tt0118998', 'tt0114436', 'tt0120657', 'tt0116213', 'tt0119738', 'tt0116583', 'tt0114924', 'tt0116695', 'tt0116996', 'tt0114508', 'tt0117218', 'tt0113749', 'tt0115685', 'tt0118617', 'tt0118607', 'tt2053425', 'tt1121931', 'tt0116483', 'tt0120902', 'tt0120907', 'tt0120915', 'tt0165929', 'tt0121765', 'tt0121766', 'tt0129167', 'tt0129387', 'tt0120762', 'tt0120888', 'tt0132347', 'tt0134119', 'tt0120755', 'tt0138097', 'tt0120780', 'tt0134084', 'tt1216487', 'tt0128442', 'tt0127536', 'tt0137363', 'tt0120789', 'tt0120783', 'tt0137523', 'tt0120770', 'tt0120913', 'tt0122690', 'tt0120815', 'tt0122933', 'tt0120855', 'tt0120794', 'tt0120889', 'tt0120903', 'tt0134847', 'tt1302011', 'tt1343727', 'tt0119081', 'tt0119099', 'tt0162222', 'tt0128445', 'tt0120873', 'tt0124298', 'tt0120053', 'tt0120791', 'tt0120832', 'tt0131857', 'tt0120669', 'tt0119468', 'tt0120686', 'tt0120338', 'tt1431045', 'tt1433811', 'tt0120461', 'tt0120784', 'tt0119925', 'tt1532503', 'tt0119217', 'tt0120655', 'tt0120738', 'tt0146316', 'tt0166924', 'tt0167261', 'tt0169102', 'tt0172493', 'tt0143145', 'tt0150377', 'tt1104001', 'tt1568338', 'tt0168629', 'tt0151738', 'tt0154420', 'tt0162346', 'tt0155267', 'tt0164184', 'tt0139809', 'tt0166896', 'tt0163651', 'tt0139239', 'tt0142688', 'tt0164334', 'tt0163988', 'tt0172156', 'tt0163978', 'tt0145531', 'tt1723811', 'tt1666801', 'tt0164912', 'tt0146675', 'tt0172495', 'tt0147612', 'tt0151804', 'tt0164052', 'tt0167190', 'tt0163187', 'tt0146882', 'tt0146336', 'tt0149261', 'tt0134273', 'tt0139134', 'tt1862079', 'tt0144117', 'tt0120863', 'tt0131325', 'tt0120917', 'tt0138749', 'tt0162661', 'tt0163025', 'tt0233469', 'tt0160862', 'tt0187078', 'tt0187738', 'tt0190590', 'tt0198781', 'tt0200465', 'tt0206634', 'tt2120120', 'tt0211915', 'tt0211933', 'tt0213847', 'tt0242423', 'tt0245674', 'tt0247638', 'tt0181536', 'tt0219699', 'tt0183790', 'tt0180093', 'tt0209475', 'tt0187393', 'tt0212720', 'tt0209163', 'tt1213644', 'tt2404463', 'tt0209144', 'tt0217505', 'tt0203019', 'tt0183523', 'tt0196229', 'tt0230030', 'tt0177789', 'tt0212338', 'tt0181865', 'tt0178868', 'tt0190865', 'tt0204946', 'tt0190138', 'tt0206314', 'tt0183649', 'tt3183660', 'tt0200550', 'tt0185183', 'tt0207201', 'tt0184894', 'tt0191397', 'tt0186566', 'tt0177971', 'tt0181852', 'tt0077975', 'tt0213149', 'tt0212346', 'tt0221027', 'tt0175142', 'tt0181689', 'tt0251736', 'tt4776998', 'tt0258153', 'tt0259324', 'tt0272152', 'tt0275847', 'tt0283111', 'tt0289043', 'tt0289879', 'tt0290334', 'tt0293564', 'tt0295701', 'tt0301357', 'tt0230838', 'tt0240772', 'tt0251127', 'tt0232500', 'tt0264395', 'tt0052618', 'tt0288477', 'tt0253474', 'tt0248667', 'tt0267804', 'tt0340163', 'tt0245844', 'tt0251075', 'tt0253754', 'tt0250687', 'tt0244244', 'tt0230600', 'tt0243736', 'tt0312004', 'tt0069704', 'tt0317219', 'tt0325703', 'tt0327084', 'tt0327597', 'tt0329774', 'tt0330373', 'tt0266915', 'tt0289765', 'tt0298814', 'tt0276919', 'tt0319262', 'tt0280590', 'tt0268380', 'tt0285823', 'tt0322330', 'tt0083944', 'tt0084827', 'tt0293662', 'tt0290673', 'tt0287978', 'tt0277296', 'tt0298130', 'tt0315733', 'tt0304415', 'tt0286788', 'tt0290095', 'tt0318462', 'tt0277027', 'tt4334266', 'tt0267913', 'tt0090605', 'tt0296572', 'tt0097165', 'tt0268978', 'tt0311289', 'tt0266987', 'tt0274166', 'tt0317705', 'tt0290002', 'tt0271027', 'tt0292490', 'tt0285742', 'tt0287467', 'tt0274558', 'tt0298148', 'tt0313737', 'tt0361862', 'tt0115963', 'tt0096438', 'tt0097428', 'tt1608290', 'tt1979388', 'tt1980209', 'tt2179116', 'tt2234155', 'tt0276751', 'tt0333780', 'tt0338348', 'tt0339291', 'tt0343737', 'tt0345950', 'tt0347149', 'tt0347304', 'tt0348150', 'tt0383216', 'tt0154506', 'tt0348333', 'tt0076786', 'tt0352248', 'tt0362478', 'tt0355295', 'tt0356634', 'tt0358273', 'tt0359950', 'tt0361748', 'tt0325710', 'tt0328828', 'tt0313542', 'tt0327850', 'tt0322259', 'tt0307479', 'tt0349903', 'tt0320661', 'tt1411250', 'tt0317648', 'tt0305224', 'tt0110322', 'tt0307453', 'tt0305711', 'tt0311113', 'tt0328538', 'tt0120768', 'tt0094332', 'tt0816462', 'tt0119567', 'tt2039393', 'tt0800320', 'tt0314331', 'tt0327554', 'tt0333766', 'tt0315983', 'tt0098258', 'tt0117998', 'tt0316654', 'tt0309698', 'tt0349683', 'tt0328832', 'tt0327679', 'tt0322802', 'tt0309987', 'tt0328107', 'tt0319343', 'tt0317740', 'tt0327056', 'tt0320691', 'tt0316396', 'tt0363771', 'tt0097778', 'tt0103855', 'tt0365686', 'tt0065421', 'tt0080339', 'tt1758830', 'tt2262227', 'tt0770703', 'tt2381249', 'tt1859650', 'tt1524930', 'tt1278340', 'tt0978762', 'tt0424095', 'tt0086200', 'tt0106611', 'tt1093908', 'tt1397514', 'tt0454945', 'tt0102926', 'tt1646971', 'tt0825232', 'tt0066026', 'tt3469046', 'tt5140878', 'tt1648190', 'tt3371366', 'tt1959563', 'tt1458169', 'tt4633690', 'tt5439796', 'tt6556890', 'tt0098554', 'tt0099077', 'tt4565520', 'tt2331047', 'tt5719700', 'tt5116504', 'tt4721404', 'tt0478970', 'tt2057392', 'tt0103874', 'tt0101272', 'tt0104257', 'tt0100507', 'tt0099487', 'tt0099582', 'tt0100263', 'tt0103873', 'tt0101410', 'tt0100758', 'tt0101761', 'tt3741834', 'tt0056801', 'tt0102138', 'tt0103639', 'tt0103786', 'tt2080374', 'tt0112740', 'tt0113243', 'tt0101414', 'tt0105112', 'tt0109506', 'tt0112461', 'tt0105695', 'tt0104797', 'tt0107798', 'tt0107048', 'tt0112641', 'tt0111280', 'tt0107120', 'tt0106308', 'tt0102492', 'tt0106519', 'tt0108394', 'tt0110357', 'tt0110989', 'tt0112851', 'tt0112682', 'tt0112817', 'tt0117951', 'tt0117381', 'tt0116367', 'tt0108525', 'tt0110216', 'tt0118694', 'tt0113277', 'tt0110632', 'tt0107808', 'tt0109040', 'tt0117438', 'tt0109444', 'tt0111503', 'tt0108052', 'tt0113492', 'tt0117731', 'tt0114709', 'tt0120689', 'tt0119116', 'tt0120630', 'tt0120082', 'tt0119008', 'tt0120484', 'tt0120587', 'tt0120681', 'tt0114214', 'tt0115751', 'tt0117500', 'tt0117318', 'tt0120177', 'tt0120611', 'tt0118883', 'tt0120623', 'tt0118842', 'tt0119164', 'tt0117333', 'tt0117887', 'tt0389790', 'tt0125659', 'tt0138524', 'tt0120890', 'tt0132477', 'tt0120749', 'tt0120885', 'tt0126886', 'tt0133952', 'tt0120812', 'tt0125439', 'tt0133152', 'tt0137494', 'tt0129290', 'tt0119174', 'tt0120324', 'tt0120616', 'tt0121164', 'tt0126029', 'tt0122151', 'tt0167404', 'tt0144084', 'tt0142342', 'tt0162650', 'tt0146838', 'tt0140352', 'tt0169547', 'tt0141926', 'tt0151137', 'tt0164181', 'tt0161081', 'tt0171804', 'tt0123755', 'tt0159097', 'tt0130827', 'tt0120787', 'tt0122718', 'tt0158983', 'tt0170016', 'tt0175880', 'tt0181316', 'tt0223897', 'tt0216216', 'tt0185014', 'tt0219965', 'tt0185431', 'tt0215750', 'tt0228750', 'tt0215129', 'tt0185125', 'tt0182789', 'tt0208003', 'tt0181875', 'tt0227445', 'tt0209958', 'tt0174856', 'tt0190332', 'tt0203009', 'tt0242653', 'tt0245574', 'tt0212985', 'tt0250797', 'tt0264616', 'tt0235198', 'tt0257076', 'tt0237534', 'tt0245562', 'tt0265349', 'tt0238380', 'tt0259446', 'tt0245429', 'tt0249462', 'tt0246578', 'tt0247745', 'tt0265666', 'tt0264472', 'tt0243155', 'tt0266543', 'tt0285492', 'tt0292963', 'tt0297284', 'tt0317919', 'tt0328880', 'tt0298203', 'tt0277434', 'tt0285531', 'tt0286112', 'tt0286106', 'tt0299977', 'tt0277371', 'tt0289848', 'tt0295297', 'tt0299658', 'tt0295700', 'tt0286716', 'tt0317303', 'tt0292506', 'tt0272020', 'tt0302886', 'tt0268695', 'tt0281358', 'tt0284490', 'tt0272338', 'tt0303816', 'tt0089881', 'tt0337978', 'tt0343818', 'tt0346491', 'tt0351283', 'tt0354899', 'tt0307901', 'tt0307987', 'tt0316356', 'tt0356680', 'tt0306047', 'tt0318627', 'tt0327437', 'tt0329101', 'tt0319061', 'tt0317198', 'tt0329575', 'tt0327162', 'tt0308644', 'tt0325805', 'tt0362120', 'tt0365830', 'tt0366548', 'tt0367594', 'tt0330793', 'tt0358082', 'tt0351977', 'tt0335245', 'tt0335438', 'tt0363547', 'tt0360486', 'tt0343135', 'tt0337921', 'tt0342258', 'tt0340855', 'tt0411061', 'tt0368794', 'tt0370263', 'tt0371746', 'tt0374546', 'tt0374887', 'tt0378109', 'tt2082197', 'tt0379725', 'tt0383028', 'tt0384680', 'tt1037705', 'tt0384793', 'tt0385752', 'tt0375679', 'tt0370986', 'tt0369339', 'tt0372784', 'tt0375912', 'tt0376541', 'tt0374536', 'tt0374900', 'tt0377109', 'tt0377471', 'tt0387131', 'tt0387877', 'tt0388795', 'tt0401445', 'tt0396269', 'tt0397101', 'tt0397535', 'tt0399146', 'tt0401711', 'tt0402022', 'tt0404203', 'tt0393162', 'tt0387564', 'tt0398017', 'tt0397065', 'tt0381681', 'tt0382628', 'tt0405296', 'tt0406816', 'tt0407304', 'tt0408790', 'tt0410297', 'tt0412019', 'tt0414055', 'tt0414852', 'tt0414993', 'tt0416315', 'tt0416508', 'tt0417741', 'tt0419887', 'tt0421054', 'tt0422720', 'tt0424136', 'tt0421082', 'tt0408236', 'tt0425210', 'tt0426931', 'tt0427309', 'tt0430357', 'tt0431197', 'tt0431308', 'tt0433035', 'tt0433383', 'tt0435651', 'tt0435761', 'tt0439815', 'tt0443272', 'tt0443489', 'tt0443649', 'tt0443706', 'tt0445934', 'tt0448694', 'tt0449059', 'tt0449467', 'tt0083907', 'tt0450278', 'tt0451279', 'tt0452625', 'tt0452694', 'tt0454848', 'tt1038988', 'tt0455967', 'tt0457430', 'tt0458352', 'tt0458525', 'tt0462200', 'tt0462504', 'tt0463854', 'tt0463998', 'tt0465538', 'tt0465602', 'tt0466342', 'tt0467406', 'tt0469641', 'tt0472062', 'tt0472181', 'tt0442933', 'tt3640424', 'tt0476964', 'tt0477071', 'tt0477051', 'tt0478134', 'tt0478311', 'tt0479884', 'tt0480687', 'tt0482571', 'tt0485947', 'tt0486551', 'tt0486946', 'tt0489237', 'tt0490215', 'tt0493430', 'tt0494238', 'tt0498353', 'tt0498399', 'tt0499549', 'tt0758758', 'tt0762107', 'tt0770828', 'tt0780536', 'tt0080761', 'tt0790628', 'tt0790686', 'tt0795368', 'tt0795461', 'tt0800308', 'tt0804461', 'tt0808151', 'tt1172049', 'tt0810819', 'tt0814314', 'tt0816442', 'tt0817177', 'tt0817538', 'tt0822854', 'tt0829482', 'tt0837562', 'tt0838283', 'tt0841046', 'tt0848537', 'tt0861689', 'tt0862846', 'tt0866439', 'tt0758746', 'tt0092890', 'tt0884328', 'tt0814022', 'tt0889573', 'tt0978764', 'tt0901476', 'tt0903624', 'tt0910936', 'tt0918927', 'tt0938283', 'tt0947798', 'tt0949731', 'tt0960731', 'tt0964517', 'tt0970452', 'tt0975645', 'tt0985694', 'tt0985699', 'tt0988047', 'tt0993842', 'tt0995039', 'tt1424381', 'tt1001526', 'tt1007029', 'tt1020072', 'tt1023111', 'tt1028528', 'tt1033575', 'tt1034314', 'tt1045658', 'tt1045778', 'tt1051904', 'tt1055369', 'tt1060277', 'tt1068680', 'tt1077258', 'tt1080016', 'tt1086772', 'tt1091722', 'tt1093357', 'tt1100089', 'tt1111422', 'tt1077368', 'tt1117385', 'tt1124035', 'tt1129442', 'tt1131734', 'tt1132626', 'tt1135503', 'tt1142977', 'tt1144884', 'tt1155056', 'tt1170358', 'tt1182345', 'tt1186830', 'tt1189073', 'tt1192628', 'tt1194173', 'tt1201167', 'tt1204342', 'tt1205537', 'tt1210166', 'tt1212419', 'tt0094737', 'tt1217613', 'tt1220198', 'tt1289401', 'tt1228705', 'tt1229340', 'tt1231587', 'tt1232776', 'tt1235166', 'tt1242422', 'tt1245112', 'tt1245492', 'tt1253864', 'tt1258197', 'tt1262416', 'tt1270262', 'tt1279935', 'tt1284575', 'tt1289406', 'tt1294226', 'tt1297919', 'tt1300851', 'tt1306980', 'tt1314655', 'tt1323045', 'tt1229822', 'tt1321511', 'tt1322269', 'tt1327194', 'tt1336608', 'tt1341167', 'tt1352824', 'tt1355644', 'tt1355683', 'tt1374992', 'tt1386697', 'tt1392190', 'tt1397280', 'tt1401152', 'tt1411238', 'tt1412386', 'tt1430132', 'tt0110005', 'tt1440728', 'tt1441395', 'tt1446192', 'tt1453405', 'tt1457767', 'tt1462758', 'tt1477076', 'tt1478964', 'tt1486192', 'tt1489889', 'tt1491044', 'tt1506999', 'tt1611224', 'tt1524137', 'tt1536044', 'tt1542344', 'tt1563738', 'tt1564367', 'tt1568911', 'tt1571222', 'tt1583420', 'tt1636826', 'tt1586752', 'tt1588173', 'tt1588334', 'tt1596350', 'tt1596363', 'tt1598778', 'tt1600195', 'tt1602620', 'tt1614989', 'tt1615065', 'tt1615147', 'tt1758692', 'tt1623205', 'tt1625346', 'tt1637688', 'tt1637725', 'tt1645170', 'tt1648179', 'tt1655460', 'tt1663202', 'tt1670345', 'tt1675192', 'tt1682180', 'tt1723121', 'tt1702439', 'tt1706620', 'tt1781769', 'tt1850457', 'tt1712261', 'tt1726592', 'tt1726669', 'tt1740707', 'tt1764234', 'tt1959490', 'tt1778304', 'tt1790864', 'tt1790885', 'tt1800241', 'tt1809398', 'tt1821549', 'tt1840309', 'tt1853728', 'tt1854564', 'tt1860353', 'tt1860357', 'tt1872194', 'tt1895587', 'tt1905041', 'tt1781922', 'tt0070328', 'tt1922777', 'tt1931533', 'tt1935179', 'tt1951261', 'tt1951265', 'tt2305051', 'tt1972779', 'tt1974419', 'tt1985949', 'tt2002718', 'tt2004420', 'tt2023587', 'tt2034800', 'tt2051879', 'tt2053463', 'tt2083383', 'tt2096672', 'tt2101341', 'tt2106476', 'tt2119532', 'tt3381008', 'tt2125608', 'tt2140373', 'tt2140479', 'tt2170593', 'tt1979320', 'tt0425061', 'tt2203939', 'tt2209418', 'tt2229499', 'tt2265171', 'tt2267998', 'tt2293640', 'tt2304933', 'tt2316204', 'tt2334649', 'tt2357129', 'tt2357291', 'tt2361509', 'tt2379713', 'tt2381111', 'tt2382009', 'tt2388715', 'tt2402157', 'tt2402927', 'tt2431286', 'tt2446980', 'tt2503944', 'tt2554274', 'tt2574698', 'tt2582782', 'tt2631186', 'tt3079380', 'tt2567026', 'tt2671706', 'tt2679042', 'tt2692904', 'tt2726560', 'tt2820852', 'tt2866360', 'tt2870756', 'tt2872732', 'tt2908446', 'tt2911666', 'tt2975578', 'tt2980592', 'tt3011894', 'tt3045616', 'tt3076658', 'tt3152624', 'tt3195644', 'tt3300542', 'tt3316960', 'tt3393786', 'tt3416742', 'tt3460252', 'tt3521164', 'tt3544112', 'tt3553976', 'tt3631112', 'tt3717490', 'tt3748528', 'tt3799694', 'tt3874544', 'tt3896198', 'tt4046784', 'tt4062536', 'tt4160708', 'tt4196776', 'tt4425200', 'tt4501244', 'tt4630562', 'tt4682786', 'tt4975722', 'tt5700672', 'tt0031381', 'tt0034492', 'tt0043265', 'tt0049730', 'tt2771200', 'tt0055254', 'tt0058385', 'tt0060196', 'tt0066995', 'tt0017136', 'tt0056217', 'tt0015864', 'tt5022702', 'tt0032551', 'tt0061722', 'tt0059742', 'tt0021884', 'tt0064276', 'tt0040897', 'tt0053291', 'tt0059578', 'tt0032553', 'tt0049833', 'tt0066206', 'tt0032455', 'tt0046183', 'tt0072271', 'tt0079574', 'tt0067116', 'tt0064665', 'tt0059800', 'tt0053472', 'tt0054047', 'tt0079116', 'tt0061418', 'tt0053779', 'tt0072890', 'tt0070379', 'tt0075686', 'tt0056218', 'tt0054997', 'tt0058150', 'tt0056172', 'tt0077631', 'tt0068473', 'tt0061811', 'tt0056193', 'tt0063350', 'tt0086034', 'tt0086979', 'tt0087277', 'tt0087884', 'tt0097523', 'tt0086541', 'tt0088128', 'tt0077766', 'tt0097757', 'tt0077651', 'tt0089880', 'tt0088258', 'tt0083511', 'tt0082398', 'tt0087843', 'tt0081573', 'tt0070666', 'tt0080120', 'tt0083131', 'tt0078841', 'tt0084787', 'tt0070511', 'tt0090728', 'tt0094291', 'tt0094889', 'tt0086393', 'tt0092086', 'tt0453556', 'tt0093437', 'tt0094862', 'tt0088170', 'tt0090305', 'tt0095631', 'tt0090329', 'tt0091042', 'tt0096283', 'tt0084503', 'tt1029234', 'tt0095765', 'tt0095953', 'tt0097733', 'tt0093010', 'tt0089755', 'tt0092005', 'tt0887883', 'tt0114369', 'tt0429493', 'tt2179136', 'tt0365737', 'tt0955308', 'tt0096969', 'tt0377092', 'tt0096895', 'tt0095159', 'tt0091763', 'tt0093409', 'tt0466909', 'tt0093058', 'tt0095963', 'tt0097441', 'tt0091790', 'tt0093822', 'tt0318649', 'tt0365907', 'tt0083866', 'tt5311514', 'tt1536537', 'tt4649466', 'tt5109784', 'tt1961175', 'tt1229238', 'tt0796366', 'tt0366551', 'tt0112471', 'tt0097216', 'tt1560747', 'tt0097493', 'tt0115734', 'tt0195714', 'tt0367089', 'tt0359013', 'tt0048424', 'tt4178092', 'tt1219827', 'tt0257044', 'tt0384806', 'tt0305357', 'tt0373051', 'tt0120188', 'tt0120804', 'tt0185937', 'tt1187064', 'tt0048280', 'tt0266308', 'tt0100150', 'tt0258463', 'tt0289992', 'tt0165798', 'tt1599348', 'tt0133093', 'tt0367882', 'tt0120844', 'tt0259711', 'tt0274812', 'tt0206275', 'tt0130018', 'tt0043014', 'tt0075860', 'tt0243133', 'tt1783232', 'tt0385307', 'tt0367959', 'tt0218967', 'tt0368709', 'tt0369436', 'tt0369610', 'tt0337563', 'tt0370032', 'tt0371257', 'tt0371606', 'tt0373469', 'tt0373889', 'tt0376136', 'tt0376994', 'tt0377818', 'tt0361596', 'tt0338095', 'tt0363163', 'tt0356470', 'tt0335119', 'tt0340377', 'tt0360717', 'tt0389860', 'tt0348836', 'tt0346156', 'tt0338337', 'tt0357277', 'tt0349710', 'tt0357413', 'tt0356721', 'tt0356618', 'tt0343660', 'tt0338751', 'tt0353969', 'tt0356910', 'tt0337741', 'tt0350258', 'tt0362227', 'tt0360201', 'tt0393109', 'tt0379786', 'tt0380389', 'tt0380510', 'tt0383574', 'tt0384537', 'tt0385002', 'tt0385700', 'tt0385880', 'tt0386032', 'tt2024432', 'tt0386117', 'tt0386140', 'tt0387808', 'tt0387898', 'tt0388125', 'tt0388482', 'tt0389557', 'tt0389722', 'tt0395584', 'tt0396171', 'tt0396555', 'tt0396752', 'tt0397313', 'tt0397892', 'tt0398808', 'tt0421073', 'tt0399201', 'tt0368891', 'tt0366627', 'tt0373883', 'tt0378194', 'tt0363988', 'tt0373926', 'tt0365748', 'tt0364517', 'tt0364725', 'tt0367110', 'tt0364569', 'tt0372183', 'tt0371246', 'tt0368447', 'tt0368909', 'tt0371724', 'tt0381061', 'tt0373074', 'tt0452702', 'tt0399295', 'tt0400717', 'tt0401383', 'tt0401729', 'tt0401855', 'tt0401997', 'tt0402399', 'tt0391198', 'tt0403702', 'tt0404032', 'tt0405094', 'tt0405422', 'tt0405508', 'tt0406375', 'tt0407887', 'tt0062622', 'tt0408306', 'tt0408345', 'tt0409182', 'tt0409459', 'tt0409847', 'tt0411477', 'tt0413099', 'tt0413267', 'tt0413300', 'tt0414387', 'tt0414982', 'tt0415306', 'tt0416236', 'tt0416320', 'tt0416449', 'tt0417148', 'tt0418279', 'tt0418689', 'tt0418763', 'tt0419706', 'tt0420294', 'tt0398286', 'tt0381707', 'tt0385004', 'tt0390521', 'tt0391304', 'tt0381849', 'tt0386588', 'tt0395699', 'tt1067106', 'tt1213663', 'tt1216475', 'tt1216492', 'tt1217209', 'tt1219289', 'tt1219342', 'tt1220634', 'tt1220719', 'tt1226229', 'tt1226273', 'tt1226753', 'tt1228987', 'tt0382077', 'tt0390022', 'tt0421239', 'tt0421715', 'tt0423294', 'tt0423977', 'tt0424345', 'tt0425112', 'tt0453451', 'tt0425123', 'tt0425413', 'tt0426592', 'tt0426883', 'tt0427152', 'tt0427229', 'tt0427392', 'tt0427470', 'tt0427944', 'tt0430922', 'tt0432021', 'tt0432283', 'tt0432348', 'tt0433362', 'tt0433387', 'tt0433400', 'tt0434409', 'tt0435625', 'tt0435705', 'tt0436697', 'tt0438097', 'tt0438488', 'tt0440963', 'tt0441773', 'tt0441909', 'tt0443274', 'tt0443453', 'tt0443543', 'tt0443680', 'tt0443701', 'tt0445922', 'tt0446029', 'tt0446755', 'tt0448011', 'tt0448157', 'tt0449010', 'tt0449088', 'tt0450188', 'tt0450232', 'tt0405159', 'tt0405325', 'tt0450259', 'tt0450314', 'tt0450385', 'tt0451079', 'tt0451094', 'tt0452594', 'tt0452608', 'tt0452623', 'tt0452637', 'tt0453562', 'tt0454876', 'tt0454921', 'tt0455590', 'tt0455824', 'tt0455944', 'tt0456554', 'tt0457510', 'tt0457513', 'tt0457939', 'tt0458339', 'tt0458481', 'tt0460740', 'tt0460791', 'tt0461770', 'tt0462322', 'tt0462465', 'tt0462538', 'tt0462590', 'tt0463034', 'tt0463985', 'tt0464141', 'tt0464154', 'tt0465234', 'tt0465551', 'tt0465580', 'tt0465624', 'tt0467197', 'tt0467200', 'tt0468489', 'tt0468492', 'tt0469494', 'tt0470752', 'tt0471042', 'tt0472033', 'tt0472043', 'tt0472160', 'tt0473075', 'tt0446059', 'tt0454841', 'tt0473705', 'tt0475276', 'tt0475394', 'tt0477302', 'tt0477347', 'tt0477348', 'tt0478087', 'tt0478304', 'tt0479143', 'tt0479952', 'tt0480242', 'tt0480255', 'tt0481141', 'tt0481369', 'tt0481499', 'tt0481536', 'tt0482572', 'tt0482606', 'tt0483607', 'tt0486576', 'tt0486655', 'tt0486822', 'tt0488120', 'tt0489049', 'tt0489099', 'tt0489270', 'tt0490204', 'tt0491152', 'tt0492044', 'tt0493464', 'tt0960144', 'tt0496806', 'tt0497116', 'tt0497465', 'tt0498380', 'tt0499448', 'tt0499556', 'tt0756683', 'tt0758730', 'tt0758752', 'tt0758766', 'tt0758774', 'tt0765429', 'tt0765443', 'tt0033563', 'tt0770752', 'tt0780511', 'tt0780521', 'tt0780571', 'tt0455407', 'tt0988595', 'tt0472399', 'tt0455760', 'tt0477080', 'tt0780653', 'tt0783233', 'tt0787475', 'tt0790636', 'tt0790724', 'tt0790736', 'tt0795351', 'tt0795421', 'tt0799934', 'tt0799949', 'tt0800039', 'tt0800369', 'tt0803096', 'tt0804497', 'tt0805564', 'tt0805570', 'tt0808279', 'tt1126590', 'tt0808417', 'tt0810913', 'tt0814255', 'tt0815236', 'tt0815241', 'tt0815245', 'tt0816692', 'tt0816711', 'tt0817230', 'tt0821640', 'tt0822832', 'tt0824747', 'tt0829150', 'tt0830515', 'tt0831887', 'tt0832266', 'tt0834001', 'tt0838221', 'tt0839980', 'tt0840361', 'tt0842926', 'tt0844471', 'tt0851578', 'tt0976051', 'tt0852713', 'tt0859163', 'tt0861739', 'tt0862856', 'tt0864761', 'tt0864835', 'tt0892782', 'tt0865556', 'tt0870111', 'tt0870984', 'tt0871510', 'tt0780504', 'tt0873886', 'tt0876563', 'tt0878804', 'tt0879870', 'tt1041829', 'tt0882977', 'tt0884732', 'tt0889583', 'tt0890870', 'tt0892318', 'tt0892769', 'tt0892791', 'tt0907657', 'tt0910970', 'tt0914798', 'tt0914863', 'tt0918940', 'tt0926084', 'tt0929632', 'tt0938330', 'tt0942385', 'tt0944835', 'tt0945513', 'tt0947810', 'tt0948470', 'tt0952640', 'tt0963178', 'tt0963794', 'tt0963966', 'tt0970179', 'tt0970411', 'tt0970866', 'tt0971209', 'tt0974661', 'tt0980970', 'tt0981227', 'tt0983193', 'tt0986233', 'tt0986263', 'tt0986264', 'tt0989757', 'tt0990407', 'tt0993846', 'tt1000774', 'tt0844708', 'tt0822847', 'tt0831387', 'tt0800080', 'tt0811080', 'tt1001508', 'tt1007028', 'tt1010048', 'tt1013743', 'tt1013752', 'tt1019452', 'tt1020530', 'tt1020558', 'tt1022603', 'tt1023114', 'tt1023481', 'tt1027718', 'tt1028532', 'tt1032755', 'tt1033643', 'tt1034032', 'tt1034303', 'tt1034331', 'tt1034389', 'tt1038686', 'tt1038919', 'tt1045772', 'tt1046173', 'tt1049413', 'tt1053424', 'tt1054606', 'tt1103153', 'tt1055292', 'tt1057500', 'tt1059786', 'tt1063669', 'tt1065073', 'tt1067583', 'tt1071875', 'tt1073498', 'tt1074638', 'tt1078912', 'tt1078940', 'tt1082868', 'tt1083452', 'tt1091191', 'tt1092026', 'tt1095217', 'tt1098327', 'tt1109624', 'tt1114740', 'tt0936501', 'tt0905372', 'tt1116184', 'tt1119646', 'tt1120985', 'tt1121096', 'tt1125849', 'tt1152398', 'tt1126591', 'tt1126618', 'tt1127180', 'tt1130080', 'tt1130884', 'tt1230414', 'tt1131729', 'tt1132620', 'tt1133985', 'tt1135985', 'tt1136608', 'tt1139328', 'tt1139797', 'tt1142988', 'tt1148204', 'tt1149362', 'tt1674771', 'tt1152836', 'tt1156398', 'tt1161864', 'tt1164999', 'tt1172233', 'tt1172570', 'tt1178663', 'tt1179034', 'tt1179904', 'tt1179933', 'tt1186367', 'tt1187043', 'tt1188729', 'tt1188996', 'tt1189340', 'tt1190080', 'tt1675434', 'tt1191111', 'tt1193138', 'tt1195478', 'tt1197624', 'tt1197628', 'tt1201607', 'tt1204975', 'tt1205489', 'tt1206543', 'tt1210042', 'tt1210819', 'tt1211837', 'tt1211956', 'tt1231583', 'tt1232200', 'tt1232829', 'tt1233227', 'tt1234548', 'tt1235124', 'tt1235522', 'tt1240982', 'tt1242432', 'tt1242460', 'tt1243957', 'tt1245526', 'tt1250777', 'tt1253863', 'tt1255953', 'tt1258972', 'tt1259521', 'tt1259571', 'tt1261945', 'tt1263670', 'tt1268799', 'tt1270798', 'tt1272878', 'tt1276104', 'tt1277953', 'tt1282140', 'tt1285016', 'tt1288558', 'tt1428538', 'tt1291584', 'tt1292566', 'tt1293847', 'tt1298649', 'tt1298650', 'tt1300854', 'tt1267297', 'tt1399103', 'tt1234721', 'tt1185416', 'tt1291150', 'tt1305806', 'tt1307068', 'tt1315981', 'tt1318514', 'tt1436045', 'tt1320253', 'tt1321870', 'tt1322312', 'tt1323594', 'tt1324999', 'tt1325004', 'tt1327773', 'tt1333125', 'tt1334260', 'tt1335975', 'tt1340138', 'tt1340800', 'tt1343097', 'tt1345836', 'tt1351685', 'tt1355630', 'tt1365050', 'tt1366344', 'tt1371111', 'tt1371150', 'tt1379182', 'tt1385826', 'tt1385867', 'tt1386588', 'tt1386932', 'tt1389137', 'tt1706593', 'tt1390411', 'tt1392170', 'tt1392214', 'tt1396218', 'tt1398426', 'tt1399683', 'tt1403981', 'tt1408101', 'tt1408253', 'tt1409024', 'tt1411697', 'tt1418377', 'tt1436562', 'tt1386703', 'tt1343092', 'tt1234719', 'tt1375670', 'tt1438254', 'tt1478338', 'tt1440129', 'tt1440292', 'tt1441952', 'tt1446714', 'tt1450321', 'tt1454029', 'tt1454468', 'tt1456635', 'tt1458175', 'tt1462041', 'tt1464540', 'tt1465522', 'tt1467304', 'tt1470827', 'tt1482459', 'tt1483013', 'tt1486834', 'tt1488555', 'tt1490017', 'tt1496025', 'tt1499658', 'tt1502404', 'tt1504320', 'tt1512235', 'tt1515091', 'tt1606389', 'tt1517260', 'tt1527186', 'tt1528100', 'tt1528854', 'tt1535108', 'tt1535109', 'tt1602613', 'tt1538403', 'tt1540133', 'tt1547234', 'tt1549572', 'tt1549920', 'tt1555149', 'tt1707386', 'tt1562872', 'tt1564585', 'tt1567609', 'tt1568346', 'tt1568921', 'tt1570728', 'tt1502712', 'tt1438176', 'tt1559547', 'tt1486185', 'tt1433108', 'tt1582507', 'tt1583421', 'tt1586265', 'tt1587310', 'tt1587707', 'tt1588170', 'tt1591095', 'tt1591479', 'tt1592525', 'tt1596343', 'tt1596365', 'tt1598822', 'tt1600196', 'tt1601913', 'tt1605630', 'tt1605717', 'tt1605783', 'tt1606378', 'tt1616195', 'tt1617661', 'tt1711425', 'tt1618442', 'tt1622547', 'tt1622979', 'tt1623288', 'tt1628841', 'tt1631867', 'tt1632708', 'tt1634122', 'tt1637706', 'tt1638002', 'tt1638355', 'tt1645089', 'tt1646987', 'tt1649419', 'tt1650062', 'tt1655420', 'tt1655441', 'tt1655442', 'tt1657507', 'tt1659337', 'tt1663662', 'tt1673434', 'tt1683526', 'tt1687901', 'tt1661199', 'tt1690953', 'tt1700841', 'tt1702443', 'tt1714915', 'tt1716772', 'tt1727388', 'tt1731141', 'tt1735898', 'tt1748122', 'tt1763303', 'tt1972571', 'tt1764651', 'tt1772341', 'tt1790809', 'tt1790886', 'tt1791528', 'tt1798709', 'tt1800246', 'tt1815862', 'tt1817273', 'tt1821694', 'tt1823672', 'tt1832382', 'tt1839492', 'tt1840417', 'tt1843866', 'tt1853739', 'tt1855199', 'tt1855325', 'tt1872181', 'tt1877832', 'tt1878870', 'tt1899353', 'tt1907668', 'tt1911644', 'tt1911658', 'tt1692486', 'tt1742334', 'tt1748179', 'tt1912398', 'tt1915581', 'tt1921064', 'tt1924396', 'tt1924429', 'tt1924435', 'tt1935859', 'tt1937390', 'tt1951264', 'tt1951266', 'tt1954470', 'tt1972591', 'tt1980929', 'tt1981115', 'tt1981677', 'tt1985966', 'tt1990314', 'tt1991245', 'tt2013293', 'tt2015381', 'tt2017038', 'tt2024469', 'tt2024544', 'tt2042568', 'tt2084970', 'tt2094766', 'tt2096673', 'tt2101441', 'tt2103281', 'tt2106361', 'tt2109184', 'tt2109248', 'tt2125435', 'tt2126355', 'tt2132285', 'tt2140379', 'tt2140619', 'tt2170439', 'tt2172934', 'tt2177771', 'tt2184339', 'tt1939659', 'tt2191701', 'tt2193215', 'tt2194499', 'tt2199571', 'tt2205697', 'tt2224026', 'tt2226417', 'tt2241351', 'tt2245084', 'tt2250912', 'tt2267968', 'tt2277860', 'tt2278388', 'tt2278871', 'tt2294449', 'tt2302755', 'tt2310332', 'tt2312718', 'tt2316411', 'tt2321549', 'tt2322441', 'tt2333784', 'tt2334873', 'tt2334879', 'tt2338151', 'tt2358891', 'tt2359024', 'tt2364841', 'tt2369135', 'tt2370248', 'tt2377322', 'tt2381991', 'tt2387433', 'tt2387559', 'tt2390361', 'tt2395427', 'tt2397535', 'tt2404233', 'tt2404311', 'tt2436386', 'tt2446042', 'tt2488496', 'tt2510894', 'tt2543164', 'tt2545118', 'tt2557490', 'tt2561572', 'tt2562232', 'tt3470600', 'tt0071562', 'tt2381941', 'tt2345759', 'tt2209764', 'tt2582496', 'tt2582802', 'tt2582846', 'tt2592614', 'tt2637276', 'tt2649554', 'tt2660888', 'tt2674426', 'tt2692250', 'tt2709768', 'tt2719848', 'tt2763304', 'tt2788710', 'tt2802144', 'tt2823054', 'tt3235888', 'tt2848292', 'tt2870612', 'tt2872718', 'tt2883512', 'tt2884206', 'tt2910814', 'tt2937898', 'tt2948356', 'tt2975590', 'tt2980516', 'tt2980648', 'tt3007512', 'tt3063516', 'tt3065204', 'tt3072482', 'tt3110958', 'tt3168230', 'tt3170832', 'tt3203606', 'tt3263904', 'tt3312830', 'tt3315342', 'tt3316948', 'tt3322364', 'tt3322940', 'tt3385516', 'tt3397884', 'tt3410834', 'tt3450958', 'tt2713180', 'tt3040964', 'tt3464902', 'tt3488710', 'tt3498820', 'tt3522806', 'tt3531824', 'tt0034583', 'tt3569230', 'tt3605418', 'tt3622592', 'tt3659388', 'tt3682448', 'tt3691740', 'tt3713166', 'tt3731562', 'tt3774114', 'tt3783958', 'tt3850214', 'tt3863552', 'tt3882082', 'tt3890160', 'tt3949660', 'tt4034228', 'tt4034354', 'tt4052882', 'tt4094724', 'tt4116284', 'tt4172430', 'tt4263482', 'tt4276820', 'tt4302938', 'tt4438848', 'tt4465564', 'tt4550098', 'tt4651520', 'tt4698684', 'tt4786282', 'tt4846340', 'tt4972582', 'tt5052448', 'tt5074352', 'tt5988370', 'tt0013442', 'tt0029583', 'tt0036775', 'tt0040522', 'tt0044079', 'tt0048545', 'tt0053198', 'tt0053285', 'tt0057012', 'tt0057076', 'tt0080455', 'tt0064757', 'tt0065214', 'tt0046250', 'tt0033467', 'tt0032904', 'tt0033870', 'tt0044706', 'tt0012349', 'tt0049406', 'tt0042192', 'tt0040746', 'tt0024216', 'tt0064116', 'tt0064115', 'tt0032910', 'tt0032976', 'tt0061512', 'tt0048728', 'tt0047296', 'tt0050825', 'tt0050976', 'tt0045152', 'tt0072431', 'tt0031679', 'tt0050083', 'tt0035423', 'tt0038650', 'tt0041959', 'tt0038355', 'tt0047478', 'tt0047396', 'tt5442430', 'tt0022100', 'tt0067992', 'tt0042332', 'tt0046912', 'tt0038787', 'tt0017925', 'tt0070034', 'tt0076759', 'tt0078346', 'tt0078748', 'tt0079470', 'tt0080684', 'tt0074958', 'tt0080749', 'tt0054215', 'tt0070735', 'tt0067185', 'tt0079817', 'tt0056592', 'tt0051201', 'tt0081505', 'tt0054331', 'tt0055630', 'tt0061852', 'tt0052357', 'tt0055614', 'tt0074119', 'tt0062512', 'tt0055031', 'tt0058461', 'tt0055928', 'tt0056869', 'tt0066999', 'tt0082495', 'tt0075005', 'tt0058331', 'tt0061184', 'tt0063442', 'tt0071315', 'tt0077928', 'tt0082198', 'tt0050986', 'tt0075314', 'tt0054698', 'tt0063522', 'tt0061578', 'tt0075148', 'tt0057546', 'tt0052311', 'tt0060827', 'tt0071853', 'tt0085333', 'tt0085959', 'tt0086006', 'tt0086190', 'tt0086567', 'tt0335266', 'tt0087544', 'tt0087928', 'tt0088161', 'tt0088939', 'tt0090264', 'tt0087363', 'tt0083658', 'tt0087182', 'tt0097576', 'tt0074486', 'tt0071360', 'tt0077416', 'tt0079417', 'tt0069293', 'tt0070917', 'tt0069762', 'tt0075029', 'tt0085334', 'tt0453467', 'tt0088323', 'tt0079501', 'tt0088847', 'tt0107818', 'tt0077402', 'tt0089218', 'tt0068646', 'tt0076752', 'tt0082340', 'tt0087078', 'tt0073195', 'tt0086066', 'tt0073486', 'tt0073629', 'tt0074285', 'tt0072684', 'tt0086250', 'tt0079944', 'tt0070047', 'tt0078788', 'tt0079522', 'tt0081398', 'tt0090756', 'tt0091064', 'tt0092563', 'tt0092991', 'tt0093105', 'tt0093748', 'tt0093773', 'tt0095705', 'tt0095956', 'tt0093870', 'tt0091605', 'tt0092644', 'tt0084516', 'tt0091369', 'tt0096061', 'tt0089927', 'tt0093779', 'tt0094012', 'tt0084726', 'tt0087800', 'tt0093177', 'tt0092965', 'tt0088846', 'tt0093191', 'tt0093389', 'tt0088993', 'tt0091419', 'tt0088930', 'tt0091326', 'tt0096754', 'tt0088944', 'tt0083929', 'tt0084805', 'tt0091167', 'tt0094625', 'tt0086960', 'tt0088247', 'tt0083987', 'tt0086465', 'tt0087803', 'tt0097742', 'tt0093894', 'tt0086879', 'tt0088011', 'tt0094226', 'tt1667889', 'tt1860213', 'tt0104431', 'tt0338013', 'tt0116365', 'tt0364045', 'tt0120891', 'tt0118715', 'tt0044081', 'tt0090859', 'tt0097239', 'tt0120601', 'tt0369441', 'tt0095327', 'tt0095647', 'tt0372588', 'tt0094721', 'tt0120746', 'tt0096256', 'tt0398165', 'tt0096734', 'tt0090863', 'tt0095489', 'tt0092067', 'tt0092675', 'tt0092099', 'tt0295178', 'tt0095016', 'tt0094898', 'tt0096320', 'tt0095031', 'tt0105690', 'tt0056923', 'tt0324216', 'tt0385267', 'tt0120693', 'tt0186151', 'tt0085995', 'tt1798684', 'tt0096928', 'tt0097351', 'tt2180411', 'tt0284837', 'tt1014759', 'tt3567288', 'tt0112870', 'tt0115798', 'tt0270288', 'tt1078588', 'tt0053604', 'tt0145681', 'tt0445990', 'tt0119345', 'tt0076666', 'tt0457400', 'tt0087332', 'tt0117060', 'tt0053125', 'tt0101452', 'tt0210945', 'tt0349205', 'tt0093629', 'tt0420223', 'tt0118571', 'tt0368008', 'tt0104070', 'tt0427327', 'tt0102798', 'tt0252076', 'tt0120632', 'tt0082694', 'tt0124315', 'tt0092007', 'tt1667353', 'tt1509767', 'tt0111255', 'tt0173840', 'tt0087469', 'tt0080678', 'tt0119822', 'tt0118655', 'tt0110622', 'tt0335345', 'tt0066921', 'tt0106977', 'tt0311429', 'tt0479997', 'tt0293508', 'tt0147800', 'tt0094947', 'tt0107614', 'tt0116225', 'tt1403865', 'tt0208092', 'tt0468569', 'tt5813916', 'tt0027977', 'tt0021749', 'tt1650554', 'tt0109830']
# sort_by_rating(temp)