function rStatus(response) {
	if (response.status >= 200 && response.status < 300) {
		return Promise.resolve(response)
	} else {
		return Promise.reject(new Error(response.statusText))
	}
}

function jsonify(response) {
	return response.text();
}

function naoTimesProcess(disID) {
	console.log("Fetching naoTimes data");
	fetch(`https://utang.naoti.me/${disID}?pretty=true`)
		.then(rStatus)
		.then(jsonify)
		.then(function (nT_data) {
			var n = new Date();
			var formatDate = function formatDate(a) {
				var s = ((a * 1000) - n) / 1000;
				var m = Math.floor(s / 60);
				var h = Math.floor(s / 60 / 60);
				var d = Math.floor(s / 60 / 60 / 24);

				if (s < 0) {
					return false;
				}

				switch (d) {
					case 0:
						if (h > 1) {
							return "Tayang dalam " + h + " jam";
						} else if (m > 1) {
							return "Tayang dalam " + m + " menit";
						} else {
							return "Tayang dalam " + s + " detik";
						}
					case 1:
						return "Tayang besok";
					default:
						return "Tayang dalam " + d + " hari";
				}
			};
			var div_data = document.getElementById("naotimes");
			var loading_elem = document.getElementById("naotimes-loading");
			var json_data = JSON.parse(nT_data);
			if (Object.keys(json_data).length == 0) {
				var h2_node = document.createElement("h2");
				h2_node.classList.add("naotimes-animetitle")
				var h2_textNode = document.createTextNode("Tidak ada data utang");
				h2_node.appendChild(h2_textNode);
				loading_elem.parentNode.removeChild(loading_elem);
				return 0;
			}
			let ordered_season_state = {};
			Object.keys(json_data).sort().reverse().forEach(function(key) {
				ordered_season_state[key] = json_data[key];
			});
			console.log("Parsing naoTimes data");
			for (let [_, season_data] of Object.entries(ordered_season_state)) {
				var h2_node = document.createElement("h2");
				h2_node.classList.add("naotimes-seasonal");
				h2_node.appendChild(document.createTextNode(season_data["name"]));
				let added_count = 0;
				let to_append_divs = [];
				season_data["data"].forEach(function (item) {
					let anime_title = item["title"];
					var statuses = item["status"];
					var current_stat = [];
					var current_episode = item["episode"];
					for (let [stat_name, stat_status] of Object.entries(statuses)) {
						if (!stat_status) {
							current_stat.push(stat_name);
						};
					};

					if (Array.isArray(current_stat) && current_stat.length) {
						current_stat = current_stat.join(" ");
						let air_time = formatDate(item["airing_time"]);
						if (air_time) {
							current_stat = air_time;
						}

						var h3_node = document.createElement("h3");
						h3_node.classList.add("naotimes-animetitle");
						var stat_node = document.createElement("ul");
						stat_node.classList.add("naotimes-animeprogress");
						if (current_episode.length < 2) { // pad number
							current_episode = "0" + current_episode;
						}
						var final_text = current_episode + " @ " + current_stat;
						stat_node.appendChild(document.createTextNode(final_text));
						h3_node.appendChild(document.createTextNode(anime_title));
						to_append_divs.push(h3_node);
						to_append_divs.push(stat_node);
						added_count += 1;
					}
				});
				if (added_count > 0) {
					div_data.appendChild(h2_node);
					to_append_divs.forEach(function (div_node) {
						div_data.appendChild(div_node);
					});
				};
			};
			loading_elem.parentNode.removeChild(loading_elem);
			console.log("Finished!")
		}).catch(function (error) {
			var loading_elem = document.getElementById("naotimes-loading");
			console.log("Request failed", error);
			var h2_node = document.createElement("h2");
			h2_node.classList.add("naotimes-animetitle")
			var h2_textNode = document.createTextNode("Tidak dapat megambil data utang.");
			h2_node.appendChild(h2_textNode);
			loading_elem.parentNode.removeChild(loading_elem);
		});
}