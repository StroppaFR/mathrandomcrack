from mathrandomcrack.mathrandomcrack import *
import unittest

class TestMathRandomCrack(unittest.TestCase):

    def test_recover_state_from_math_random_doubles(self):
        known_doubles = [0.5167222737819601, 0.6051313728404477, 0.22425498430450674, 0.23438544548454465]

        expected_next = [0.24058273108448502, 0.7071632987915342, 0.7364176754416083, 0.9429174628720893, 0.14463954087461772, 0.46690388204928257, 0.5679465252410643, 0.057808030482194184, 0.7653512491099053, 0.4423105204008999, 0.32394431542177426, 0.17430067774632363, 0.9162234761704138, 0.8614924077878654, 0.5725599101643395, 0.8358935843656736, 0.8739140745431142, 0.41428022100362094, 0.9575789275498869, 0.3259361741900366, 0.0864629375015884, 0.5795087595623722, 0.7197928699840308, 0.6150494448029389, 0.24357820834222532, 0.9718673657131978, 0.5664468219431693, 0.3997006489009376, 0.03347361076455235, 0.7903391889138744, 0.7467833151736378, 0.800893869472477, 0.24504355181355342, 0.10085462519361887, 0.8235361528239129, 0.01680371878229936, 0.29965372111482247, 0.09540919242087664, 0.5663426835696472, 0.6341077288449175, 0.6754921219583394, 0.30087104613638327, 0.4777391681664256, 0.7582024286119369, 0.1314148427639732, 0.8823140870714286, 0.10107145907477744, 0.8063030496288934, 0.5042257712387552, 0.6276445313423586, 0.8170427012084529, 0.1770422890956982, 0.7742555412968606, 0.8633456483429791, 0.6380389595418361, 0.40035320454454504, 0.008949968676235542, 0.5448286455627345, 0.7466638340091585, 0.1886293907130161, 0.3032947493696152, 0.5768133319298463, 0.8532588502311245, 0.8787744833141198, 0.7394620812648265, 0.44394709733857196, 0.2280429557622825, 0.15499131959613877, 0.7241390518277382, 0.10811525833845659, 0.9268626345052817, 0.15829442368373758, 0.31919551378468536, 0.6080300865704606, 0.9535055449405643, 0.41837775923674436, 0.20529957653515907, 0.5820495833564865, 0.25813566316138203, 0.5578002156099406, 0.9760324009766301, 0.3859601122545602, 0.9358865565246022, 0.09853906388451228, 0.12817666982264497, 0.7512422770823941, 0.82639100545096, 0.8191270541527997, 0.29666427234430404, 0.989096451298557, 0.5851415558951292, 0.9193124192070301, 0.5663716711248832, 0.8750940093952984, 0.5275379381911538, 0.42702246194673, 0.7504828173008533, 0.5896473209096103, 0.9618747983218028, 0.7777330464887067]

        found_correct_state = False
        for recovered_math_random in recover_state_from_math_random_doubles(known_doubles):
            # Verify that the state indeed generates the correct doubles
            for d in known_doubles:
                self.assertEqual(recovered_math_random.next(), d)
            # Check if it generates the expected next doubles
            found_correct_state = all(d == recovered_math_random.next() for d in expected_next)
            if found_correct_state:
                break
        self.assertTrue(found_correct_state)

    def test_recover_state_from_math_random_doubles_scattered(self):
        generated_doubles = [0.9317818247293228, 0.10390550168686419, 0.07305787812831155, 0.8899228479633123, 0.9678643972867931, 0.8923801111068459, 0.9981769231353597, 0.01952923788544858, 0.6422523703031464, 0.3680624955677494]
        # Only keep some of the generated values, knowing which ones
        positions = [0, 4, 5, 9]
        known_doubles = [generated_doubles[ind] for ind in positions]

        expected_next = [0.8764995458510205, 0.531666065682733, 0.37750715273883495, 0.8562629292145478, 0.8442254530076962, 0.6985721224895804, 0.32141914614843325, 0.4816754589892047, 0.5626628068515391, 0.7406806158123047, 0.8467934081871875, 0.9125081956160326, 0.7707821075104102, 0.8772501704965749, 0.4132587071686529, 0.13110848180112722, 0.43181087393905404, 0.41436602409652856, 0.9462215856826626, 0.15478226529368255, 0.6028931513192419, 0.2482298027086367, 0.9118671774280918, 0.10927436361601828, 0.866819880638716, 0.034044838819265344, 0.4747242540309755, 0.8429812970517292, 0.8417182533023033, 0.15344943478556838, 0.32376225423789085, 0.5240914763426343, 0.0787777606790554, 0.509486444494323, 0.8300917459561967, 0.5261785762247104, 0.9506889140815769, 0.5739732865407203, 0.4274745047468431, 0.20866987617419563, 0.1469697345064096, 0.7326535785023955, 0.8512207604821072, 0.019447255233857152, 0.0940586053906376, 0.45788638751812893, 0.14944842990056806, 0.7816096075947794, 0.4803245759743189, 0.2644015482193578, 0.4371772216174523, 0.9092153033839947, 0.8118088585224121, 0.13822150437510072, 0.13323543158737516, 0.17925562551404162, 0.2757268293899715, 0.6868651828916292, 0.31912335424937677, 0.8571641617656351, 0.7057941250743915, 0.9664930816176194, 0.2012105510808797, 0.5414774783143428, 0.16710324020067402, 0.8342887711671767, 0.3812208887662982, 0.9427435679461424, 0.8964666676448301, 0.36817065366101187, 0.6647610743878958, 0.5579445933556737, 0.9846596535827048, 0.7350555429792642, 0.03628829561818159, 0.1417507609279809, 0.7530182515150505, 0.7302586280243459, 0.8349375350112285, 0.6651053154058528, 0.6812861941632109, 0.3949772572116985, 0.39139541205059625, 0.691223227352157, 0.3000285141328991, 0.2812374512540796, 0.858307935551369, 0.11213558956224112, 0.1391606203662754, 0.211241130264322, 0.8114566626181039, 0.4288525080214811, 0.7268366927227243, 0.5914029184477438, 0.7819026584566435, 0.27544142017644124, 0.6053317880119988, 0.4429720254022509, 0.30984337849085297, 0.7737307511930631]
        
        found_correct_state = False
        for recovered_math_random in recover_state_from_math_random_doubles(known_doubles, positions):
            # Verify that the state indeed generates the correct doubles
            for d in generated_doubles:
                self.assertEqual(recovered_math_random.next(), d)
            # Check if it generates the expected next doubles
            found_correct_state = all(d == recovered_math_random.next() for d in expected_next)
            if found_correct_state:
                break
        self.assertTrue(found_correct_state)

    def test_recover_state_from_math_random_scaled_values(self):
        factor = 36
        translation = 1
        known_values = [29, 17, 23, 22, 14, 12, 19, 20, 18, 21, 2, 15, 35, 35, 36, 8, 1, 15, 11, 3, 23, 19, 13, 4, 2, 30, 2, 2, 2, 26, 32, 1, 13, 16, 2, 18, 14, 2, 11, 17, 5, 10, 2, 1, 19, 31, 32, 5, 23, 19, 31, 36, 9, 12, 35, 2, 31, 3, 2, 14, 35, 17, 34, 7, 12, 7, 19, 25, 32]
        expected_next = [0.7919604476949207, 0.7189805118782873, 0.4405953895622283, 0.4391770030638633, 0.17691185228820938, 0.8699126856323054, 0.15011821202436137, 0.4863798042636329, 0.6883895298653904, 0.49344917522809184, 0.42035587409363595, 0.5735891494412744, 0.29613956181399903, 0.88770368432154, 0.5809508842469815, 0.8403683457798121, 0.7621963622591448, 0.5161332563082601, 0.8460613040539942, 0.2862373692637614, 0.47812758931736865, 0.37831334209743384, 0.8277681811435231, 0.7046397958522914, 0.22256652985008984, 0.4301253419938518, 0.8454293676341751, 0.3696015965775814, 0.892369077777782, 0.5674723590090738, 0.5375914558103418, 0.32517687040046495, 0.4312221653629198, 0.6650492656534395, 0.2341899871089872, 0.2539357918773506, 0.9734408276879534, 0.7328891771257453, 0.2378234259305465, 0.6354081806875982, 0.04831440098854922, 0.9200959529252273, 0.5124046080631834, 0.29498995986768106, 0.548625501269898, 0.16001128358916206, 0.4153113136221869, 0.7678661971393126, 0.21219868611984039, 0.29119595526559383, 0.9152692065515358, 0.7718317980512721, 0.8166216606475398, 0.049923431301262644, 0.7817273241652387, 0.9651366713438856, 0.5421808612304104, 0.2079278570119194, 0.9770689335854321, 0.8613163323110451, 0.6334695521043174, 0.08310255929539201, 0.13645477104696035, 0.3470476192606051, 0.2537114893888097, 0.7860421915850326, 0.0947033846588008, 0.3097570679531232, 0.3786722680138712, 0.06024684049923801, 0.11804824398975455, 0.6149490532579525, 0.7199445046047401, 0.9795149415193294, 0.9354258393705515, 0.6709029369397788, 0.6713188809298283, 0.26252070217611845, 0.6433270333189087, 0.13221153913301342, 0.4540198973034981, 0.06408289332044625, 0.28450467276052716, 0.43754353033732785, 0.741129818105303, 0.1737642147415699, 0.6617756153773962, 0.1169887300990533, 0.9333383266198447, 0.005770915376969388, 0.9645398973826833, 0.18577132751110215, 0.5427425296873281, 0.8911974734406771, 0.050428317038052395, 0.14145586499101426, 0.9505027362804166, 0.6392031259618796, 0.5997994884285773, 0.8982754796085852]

        found_correct_state = False
        for recovered_math_random in recover_state_from_math_random_scaled_values(known_values, factor, translation):
            # Verify that the state indeed generates the correct integers
            for d in known_values:
                self.assertEqual(round(factor * recovered_math_random.next() + translation), d)
            # Check if it generates the expected next doubles
            found_correct_state = all(d == recovered_math_random.next() for d in expected_next)
            if found_correct_state:
                break
        self.assertTrue(found_correct_state)

