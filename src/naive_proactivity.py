
class Naive():

    def select_action_to_play(self, plan):
        els = list(plan)
        strs = "Robot said : You should " + str(plan[els[0]][0])

        return strs
