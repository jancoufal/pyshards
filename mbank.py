import re

GPC_FILE = r"d:\doc\mBank\gpc\mKonto_09951156_161003_191003.gpc"

TYPE_REGEXES = {
	"074": re.compile(r"""^
		(?P<record_type>\d{3})
		(?P<account_number>\d{16})
		(?P<client_short_name>.{20})
		(?P<old_balance_date>\d{6})
		(?P<old_balance>\d{14})
		(?P<old_balance_sign>[+\-])
		(?P<new_balance>\d{14})
		(?P<new_balance_sign>[+\-])
		(?P<turnover_debit>\d{14})
		(?P<turnover_debit_sign>[0+\-])
		(?P<turnover_credit>\d{14})
		(?P<turnover_credit_sign>[0+\-])
		(?P<order_number>\d{3})
		(?P<transaction_date>\d{6})
		(?P<filler>.*)$""", re.VERBOSE),
	"075": re.compile(r"""^
		(?P<record_type>\d{3})
		(?P<account_number_src>\d{16})
		(?P<account_number_dst>\d{16})
		(?P<transaction_number>.{13})
		(?P<amount>\d{12})
		(?P<accounting_type>\d)
		(?P<v_symbol>.{10})
		(?P<k_symbol>.{10})
		(?P<s_symbol>.{10})
		(?P<date>\d{6})
		(?P<additional_data>.{20})
		(?P<item_change_code>.)
		(?P<data_category_r>.)
		(?P<data_category_moo>\d{3})
		(?P<due_date>\d{6})$""", re.VERBOSE),
	"078": re.compile(r"""^
		(?P<record_type>\d{3})
		(?P<field_av1>.{35})
		(?P<field_av2>.{35})$""", re.VERBOSE),
	"079": re.compile(r"""^
		(?P<record_type>\d{3})
		(?P<field_av3>.{35})
		(?P<field_av4>.{35})$"""),
}

SANITIZE_MAP = {
	"&amp;": "&",
	# "'": "''",
}


def main():
	with open(GPC_FILE, "rt", encoding="windows-1250") as fd:
		for line in fd.readlines():
			# first three characters determines the record type
			rec_type = line[0:3]
			data_map = TYPE_REGEXES[rec_type].search(sanitize_line(line)).groupdict()

			data_string = None
			if rec_type == "074":
				data_string = format_074(data_map)
			if rec_type == "075":
				data_string = format_075(data_map)

			if data_string is not None:
				print(data_string)


def sanitize_line(line):
	ret = line.strip()
	for k in SANITIZE_MAP.keys():
		ret = ret.replace(k, SANITIZE_MAP[k])
	return ret


def format_074(data_map):
	d = data_map
	return f"{d['account_number']}" \
		f"{d['client_short_name'].strip()}" \
		f"{d['old_balance_date']}" \
		f"{d['old_balance_sign']}" \
		f"{int(d['old_balance'])}" \
		f"{d['new_balance_sign']}" \
		f"{d['new_balance']}" \
		f"{d['turnover_debit_sign']}" \
		f"{d['turnover_debit']}" \
		f"{d['turnover_credit_sign']}" \
		f"{d['turnover_credit']}" \
		f"{d['order_number']}" \
		f"{d['transaction_date']}"


def format_075(data_map):
	d = data_map

	amount = int(d['amount'])
	if d['accounting_type'] == "1":
		amount = -amount

	return f"insert into t075(trn_no,amount,date,description) values({int(d['transaction_number'])},{amount},'{d['date']}','{d['additional_data'].strip()}');"


if __name__ == "__main__":
	main()
