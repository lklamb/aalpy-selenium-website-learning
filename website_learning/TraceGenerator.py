import website_learning.Settings as Settings
import website_learning.Util as Util
from website_learning.Constants import SEPARATOR_BASIC, outputs_without_page_change


class TraceGenerator:
    def __init__(self, sul):
        self.input_traces = []
        self.io_traces = []
        self.sul = sul

        self.generate_traces()
        Util.write_input_traces_to_file(self.input_traces)
        Util.write_io_traces_to_file(self.io_traces)

    # exhaustive with filtering, up to trace_len from Settings
    def generate_traces(self):
        valid_prefixes = [[]]  # initialise with prefix length 0
        for length in range(Settings.trace_len):
            Util.logger.info(SEPARATOR_BASIC)
            Util.logger.info("generating traces with length " + str(length + 1))
            new_valid_prefixes = []
            for prefix in valid_prefixes:
                page_before_last_step = Util.initial_url
                for io in reversed(prefix):
                    if not io[1] in outputs_without_page_change:
                        page_before_last_step = io[1]
                        break
                invalid_input_count = 0
                for input_letter in Util.input_alphabet:
                    if not input_letter.startswith(page_before_last_step):
                        invalid_input_count += 1
                        continue
                    io_trace = []
                    self.sul.pre()
                    for io in prefix:
                        self.sul.step(io[0])
                        io_trace.append(io)
                    output = self.sul.step(input_letter)
                    io_trace.append((input_letter, output))
                    new_valid_prefixes.append(io_trace)
                if invalid_input_count == len(Util.input_alphabet):
                    self.io_traces.append(prefix)
            if len(new_valid_prefixes) == 0:
                Util.logger.info("Maximum found valid trace length " + str(length) + " is smaller than defined trace length, terminating trace generation")
                break
            valid_prefixes = new_valid_prefixes
        self.io_traces.extend(valid_prefixes)
        for io_trace in self.io_traces:
            input_trace = []
            for io in io_trace:
                input_trace.append(io[0])
            self.input_traces.append(input_trace)
        Util.logger.info(SEPARATOR_BASIC)
