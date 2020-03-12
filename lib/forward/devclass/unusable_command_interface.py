"""
def auto_execute(self):
    # regx compile
    _promptKey = prompt.keys()
    for key in _promptKey:
        prompt[key] = re.compile(prompt[key])
    result = {
        'status': False,
        'content': '',
        'errLog': '',
        "state": None
    }
    if self.isLogin is False:
        result['errLog'] = '[Execute Error]: device not login.'
        return result
    # Setting timeout.
    self.shell.settimeout(timeout)
    # Parameters check
    parameterFormat = {
        "success": "regular-expression-success",
        "error": "regular-expression-error"
    }
    if (cmd is None) or (not isinstance(prompt, dict)) or (not isinstance(timeout, int)):
        raise ForwardError("You should given a parameter for prompt such as: %s" % (str(parameterFormat)))
    # Clean buffer data.
    while self.shell.recv_ready():
        self.shell.recv(1024)
    try:
        # send a command
        self.shell.send("{cmd}\r".format(cmd=cmd))
    except Exception:
        # break, if faild
        result["errLog"] = "That forwarder has sent a command is failed."
        return result
    isBreak = False
    while True:
        # Remove special characters.
        result["content"] = re.sub("", "", result["content"])
        self.getMore(result["content"])
        try:
            result["content"] += self.shell.recv(204800)
        except Exception:
            result["errLog"] = "Forward had recived data timeout. [%s]" % result["content"]
            return result
        # Check if all the command results have been returned
        xPrompt = re.search(self.basePrompt, re.sub(self.moreFlag, "", result["content"].split("\r\n")[-1]))
        if xPrompt:
            xPrompt = xPrompt.group().strip(" ")
            # The all command results may have been returned.
            # Send a key of enter to reconfirm.
            self.shell.send("\r")
            tmp = self.shell.recv(512)
            yPrompt = re.search(self.basePrompt, re.sub(self.moreFlag, "", tmp.split("\r\n")[-1]))
            if yPrompt:
                # Formate prompt.
                yPrompt = yPrompt.group().strip(" ")
                # Compare two host prompts for consistency
                if xPrompt == yPrompt:
                    # Confirmed.
                    # [ex] GD-N7010-S2 #
                    # [ex] GD-N7010-S2 #
                    break
                else:
                    # The all command results have been not returned yet,so continue
                    result["content"] += tmp
                    continue
            else:
                # The all command results have been not returned yet,so continue
                result["content"] += tmp
                continue
        else:
                # The all command results have been not returned yet,so continue
            continue
    # Mathing specify key
    for key in prompt:
        if re.search(prompt[key], re.sub(self.moreFlag, "", result["content"])):
            # Found it
            result["state"] = key
            isBreak = True
            break
    # Delete page break
    result["content"] = re.sub("\r\n.*?\r *?\r", "\r\n", result["content"])
    # Clearing special characters
    result["content"] = re.sub(" *---- More ----\x1b\[42D                                          \x1b\[42D",
                                "",
                                result["content"])
    result["content"] = re.sub("<--- More --->\\r +\\r", "", result["content"])
    # remove the More charactor
    result["content"] = re.sub(' \-\-More\(CTRL\+C break\)\-\- (\x00|\x08){0,} +(\x00|\x08){0,}', "",
                                result["content"])
    # remove the space key
    result["content"] = re.sub("(\x08)+ +", "", result["content"])
    result["status"] = True
    return result
"""


def command(self, cmd=None, prompt={}, timeout=30):
    """execute a command line, powerful and suitable for any scene,
    but need to define whole prompt dict list
    """
    # regx compile
    # _promptKey = prompt.keys()
