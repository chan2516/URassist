window.addEventListener("load", windowLoadHandler, false);
var sphereRad = 140;
var radius_sp = 1;
//for debug messages
var Debugger = function () { };
Debugger.log = function (message) {
	try {
		console.log(message);
	}
	catch (exception) {
		return;
	}
}

function windowLoadHandler() {
	canvasApp();
}

function canvasSupport() {
	return Modernizr.canvas;
}

function canvasApp() {
	if (!canvasSupport()) {
		return;
	}

	var theCanvas = document.getElementById("canvasOne");
	var context = theCanvas.getContext("2d");

	var displayWidth;
	var displayHeight;
	var timer;
	var wait;
	var count;
	var numToAddEachFrame;
	var particleList;
	var recycleBin;
	var particleAlpha;
	var r, g, b;
	var fLen;
	var m;
	var projCenterX;
	var projCenterY;
	var zMax;
	var turnAngle;
	var turnSpeed;
	var sphereCenterX, sphereCenterY, sphereCenterZ;
	var particleRad;
	var zeroAlphaDepth;
	var randAccelX, randAccelY, randAccelZ;
	var gravity;
	var rgbString;
	//we are defining a lot of variables used in the screen update functions globally so that they don't have to be redefined every frame.
	var p;
	var outsideTest;
	var nextParticle;
	var sinAngle;
	var cosAngle;
	var rotX, rotZ;
	var depthAlphaFactor;
	var i;
	var theta, phi;
	var x0, y0, z0;

	init();

	// eel.expose(init)
	function init() {
		wait = 1;
		count = wait - 1;
		numToAddEachFrame = 8;

		//particle color
		r = 0;
		g = 72;
		b = 255;

		rgbString = "rgba(" + r + "," + g + "," + b + ","; //partial string for color which will be completed by appending alpha value.
		particleAlpha = 1; //maximum alpha

		displayWidth = theCanvas.width;
		displayHeight = theCanvas.height;

		fLen = 320; //represents the distance from the viewer to z=0 depth.

		//projection center coordinates sets location of origin
		projCenterX = displayWidth / 2;
		projCenterY = displayHeight / 2;

		//we will not draw coordinates if they have too large of a z-coordinate (which means they are very close to the observer).
		zMax = fLen - 2;

		particleList = {};
		recycleBin = {};

		//random acceleration factors - causes some random motion
		randAccelX = 0.1;
		randAccelY = 0.1;
		randAccelZ = 0.1;

		gravity = -0; //try changing to a positive number (not too large, for example 0.3), or negative for floating upwards.

		particleRad = 1.8;

		sphereCenterX = 0;
		sphereCenterY = 0;
		sphereCenterZ = -3 - sphereRad;

		//alpha values will lessen as particles move further back, causing depth-based darkening:
		zeroAlphaDepth = -750;

		turnSpeed = 2 * Math.PI / 1200; //the sphere will rotate at this speed (one complete rotation every 1600 frames).
		turnAngle = 0; //initial angle

		timer = setInterval(onTimer, 10 / 24);
	}

	function onTimer() {
		//if enough time has elapsed, we will add new particles.		
		count++;
		if (count >= wait) {

			count = 0;
			for (i = 0; i < numToAddEachFrame; i++) {
				theta = Math.random() * 2 * Math.PI;
				phi = Math.acos(Math.random() * 2 - 1);
				x0 = sphereRad * Math.sin(phi) * Math.cos(theta);
				y0 = sphereRad * Math.sin(phi) * Math.sin(theta);
				z0 = sphereRad * Math.cos(phi);

				//We use the addParticle function to add a new particle. The parameters set the position and velocity components.
				//Note that the velocity parameters will cause the particle to initially fly outwards away from the sphere center (after
				//it becomes unstuck).
				var p = addParticle(x0, sphereCenterY + y0, sphereCenterZ + z0, 0.002 * x0, 0.002 * y0, 0.002 * z0);

				//we set some "envelope" parameters which will control the evolving alpha of the particles.
				p.attack = 50;
				p.hold = 50;
				p.decay = 100;
				p.initValue = 0;
				p.holdValue = particleAlpha;
				p.lastValue = 0;

				//the particle will be stuck in one place until this time has elapsed:
				p.stuckTime = 90 + Math.random() * 20;

				p.accelX = 0;
				p.accelY = gravity;
				p.accelZ = 0;
			}
		}

		//update viewing angle
		turnAngle = (turnAngle + turnSpeed) % (2 * Math.PI);
		sinAngle = Math.sin(turnAngle);
		cosAngle = Math.cos(turnAngle);

		//background fill
		context.fillStyle = "#000000";
		context.fillRect(0, 0, displayWidth, displayHeight);

		//update and draw particles
		p = particleList.first;
		while (p != null) {
			//before list is altered record next particle
			nextParticle = p.next;

			//update age
			p.age++;

			//if the particle is past its "stuck" time, it will begin to move.
			if (p.age > p.stuckTime) {
				p.velX += p.accelX + randAccelX * (Math.random() * 2 - 1);
				p.velY += p.accelY + randAccelY * (Math.random() * 2 - 1);
				p.velZ += p.accelZ + randAccelZ * (Math.random() * 2 - 1);

				p.x += p.velX;
				p.y += p.velY;
				p.z += p.velZ;
			}

			/*
			We are doing two things here to calculate display coordinates.
			The whole display is being rotated around a vertical axis, so we first calculate rotated coordinates for
			x and z (but the y coordinate will not change).
			Then, we take the new coordinates (rotX, y, rotZ), and project these onto the 2D view plane.
			*/
			rotX = cosAngle * p.x + sinAngle * (p.z - sphereCenterZ);
			rotZ = -sinAngle * p.x + cosAngle * (p.z - sphereCenterZ) + sphereCenterZ;
			m = radius_sp * fLen / (fLen - rotZ);
			p.projX = rotX * m + projCenterX;
			p.projY = p.y * m + projCenterY;

			//update alpha according to envelope parameters.
			if (p.age < p.attack + p.hold + p.decay) {
				if (p.age < p.attack) {
					p.alpha = (p.holdValue - p.initValue) / p.attack * p.age + p.initValue;
				}
				else if (p.age < p.attack + p.hold) {
					p.alpha = p.holdValue;
				}
				else if (p.age < p.attack + p.hold + p.decay) {
					p.alpha = (p.lastValue - p.holdValue) / p.decay * (p.age - p.attack - p.hold) + p.holdValue;
				}
			}
			else {
				p.dead = true;
			}

			//see if the particle is still within the viewable range.
			if ((p.projX > displayWidth) || (p.projX < 0) || (p.projY < 0) || (p.projY > displayHeight) || (rotZ > zMax)) {
				outsideTest = true;
			}
			else {
				outsideTest = false;
			}

			if (outsideTest || p.dead) {
				recycle(p);
			}

			else {
				//depth-dependent darkening
				depthAlphaFactor = (1 - rotZ / zeroAlphaDepth);
				depthAlphaFactor = (depthAlphaFactor > 1) ? 1 : ((depthAlphaFactor < 0) ? 0 : depthAlphaFactor);
				context.fillStyle = rgbString + depthAlphaFactor * p.alpha + ")";

				//draw
				context.beginPath();
				context.arc(p.projX, p.projY, m * particleRad, 0, 2 * Math.PI, false);
				context.closePath();
				context.fill();
			}

			p = nextParticle;
		}
	}

	function addParticle(x0, y0, z0, vx0, vy0, vz0) {
		var newParticle;
		var color;

		//check recycle bin for available drop:
		if (recycleBin.first != null) {
			newParticle = recycleBin.first;
			//remove from bin
			if (newParticle.next != null) {
				recycleBin.first = newParticle.next;
				newParticle.next.prev = null;
			}
			else {
				recycleBin.first = null;
			}
		}
		//if the recycle bin is empty, create a new particle (a new ampty object):
		else {
			newParticle = {};
		}

		//add to beginning of particle list
		if (particleList.first == null) {
			particleList.first = newParticle;
			newParticle.prev = null;
			newParticle.next = null;
		}
		else {
			newParticle.next = particleList.first;
			particleList.first.prev = newParticle;
			particleList.first = newParticle;
			newParticle.prev = null;
		}

		//initialize
		newParticle.x = x0;
		newParticle.y = y0;
		newParticle.z = z0;
		newParticle.velX = vx0;
		newParticle.velY = vy0;
		newParticle.velZ = vz0;
		newParticle.age = 0;
		newParticle.dead = false;
		if (Math.random() < 0.5) {
			newParticle.right = true;
		}
		else {
			newParticle.right = false;
		}
		return newParticle;
	}

	function recycle(p) {
		//remove from particleList
		if (particleList.first == p) {
			if (p.next != null) {
				p.next.prev = null;
				particleList.first = p.next;
			}
			else {
				particleList.first = null;
			}
		}
		else {
			if (p.next == null) {
				p.prev.next = null;
			}
			else {
				p.prev.next = p.next;
				p.next.prev = p.prev;
			}
		}
		//add to recycle bin
		if (recycleBin.first == null) {
			recycleBin.first = p;
			p.prev = null;
			p.next = null;
		}
		else {
			p.next = recycleBin.first;
			recycleBin.first.prev = p;
			recycleBin.first = p;
			p.prev = null;
		}
	}
}


$(function () {
	$("#slider-range").slider({
		range: false,
		min: 20,
		max: 500,
		value: 280,
		slide: function (event, ui) {
			console.log(ui.value);
			sphereRad = ui.value;
		}
	});
});

$(function () {
	$("#slider-test").slider({
		range: false,
		min: 1.0,
		max: 2.0,
		value: 1,
		step: 0.01,
		slide: function (event, ui) {
			radius_sp = ui.value;
		}
	});
});


function openSettingsDrawer() {
	const pane = document.getElementById("settings-pane");
	const overlay = document.getElementById("settings-overlay");
	pane.classList.add("open");
	overlay.classList.add("show");
	pane.setAttribute("aria-hidden", "false");
}

function closeSettingsDrawer() {
	const pane = document.getElementById("settings-pane");
	const overlay = document.getElementById("settings-overlay");
	pane.classList.remove("open");
	overlay.classList.remove("show");
	pane.setAttribute("aria-hidden", "true");
}

function bindSettingsEvents() {
	document.getElementById("SettingsBtn").addEventListener("click", openSettingsDrawer);
	document.getElementById("close-btn").addEventListener("click", closeSettingsDrawer);
	document.getElementById("settings-overlay").addEventListener("click", closeSettingsDrawer);

	const rateInput = document.getElementById("speech-rate");
	const rateLabel = document.getElementById("speech-rate-value");
	rateInput.addEventListener("input", function () {
		rateLabel.textContent = String(rateInput.value);
	});

	document.getElementById("save-settings-btn").addEventListener("click", function () {
			const aiProvider = document.getElementById("ai-provider").value;
		const speechRate = parseInt(document.getElementById("speech-rate").value, 10);
		const micDeviceIndex = parseInt(document.getElementById("mic-device").value, 10);
		const status = document.getElementById("settings-save-status");

		status.textContent = "Saving...";

			eel.save_app_settings(aiProvider, speechRate, "0", micDeviceIndex)(function (response) {
			if (response && response.success) {
				status.textContent = "Saved. Voice and AI settings are active now.";
			} else {
				status.textContent = "Could not save settings. Please try again.";
			}
		});
	});

		document.getElementById("save-provider-btn").addEventListener("click", function () {
			const provider = document.getElementById("new-provider").value;
			const apiKey = document.getElementById("new-provider-key").value.trim();
			const model = document.getElementById("new-provider-model").value.trim();
			const status = document.getElementById("settings-save-status");

			if (!apiKey) {
				status.textContent = "Please enter an API key before saving.";
				return;
			}

			status.textContent = "Saving provider key...";
			eel.add_provider_api_key(provider, apiKey, model)(function (response) {
				if (response && response.success) {
					document.getElementById("new-provider-key").value = "";
					status.textContent = "Provider key saved successfully.";
					loadAppSettings();
				} else {
					status.textContent = (response && response.message) || "Could not save provider key.";
				}
			});
		});

	document.addEventListener("keydown", function (event) {
		if (event.key === "Escape") {
			closeSettingsDrawer();
		}
	});
}

function providerLabel(providerName, modelName) {
	const provider = String(providerName || "").trim();
	const model = String(modelName || "").trim();
	return model ? `${provider} (${model})` : provider;
}

function escapeHtml(value) {
	return String(value || "")
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/\"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

function removeProvider(providerName) {
	const status = document.getElementById("settings-save-status");
	eel.remove_provider_api_key(providerName)(function (response) {
		if (response && response.success) {
			status.textContent = `${providerName} removed.`;
			loadAppSettings();
		} else {
			status.textContent = (response && response.message) || "Could not remove provider.";
		}
	});
}

window.removeProvider = removeProvider;

function renderProviderSettings(settings) {
	const providerSelect = document.getElementById("ai-provider");
	const providerList = document.getElementById("provider-list");
	const selectedProvider = settings.selected_provider || "";
	const providers = Array.isArray(settings.providers) ? settings.providers : [];

	providerSelect.innerHTML = `<option value="">Default Web Search</option>`;
	providerList.innerHTML = "";

	providers.forEach(function (entry) {
		const provider = String(entry.provider || "").trim();
		const model = String(entry.model || "").trim();
		if (!provider) {
			return;
		}

		const option = document.createElement("option");
		option.value = provider;
		option.textContent = providerLabel(provider, model);
		providerSelect.appendChild(option);

		const li = document.createElement("li");
		li.innerHTML = `<span>${escapeHtml(providerLabel(provider, model))}</span>
						<button class='delete-btn' onclick='removeProvider("${escapeHtml(provider)}")'>Remove</button>`;
		providerList.appendChild(li);
	});

	providerSelect.value = selectedProvider;
}

function renderMicrophoneSettings(settings) {
	const micSelect = document.getElementById("mic-device");
	const selectedMic = Number(settings.mic_device_index ?? -1);
	const microphones = Array.isArray(settings.microphone_devices) ? settings.microphone_devices : [];

	micSelect.innerHTML = `<option value="-1">System Default</option>`;

	microphones.forEach(function (device) {
		const index = Number(device.index);
		if (Number.isNaN(index)) {
			return;
		}

		const option = document.createElement("option");
		option.value = String(index);
		const label = device.is_default ? `${device.name} (Default)` : String(device.name || `Microphone ${index}`);
		option.textContent = label;
		micSelect.appendChild(option);
	});

	micSelect.value = String(selectedMic);
}

function loadAppSettings() {
	eel.get_app_settings()(function (settings) {
		if (!settings) {
			return;
		}

		renderProviderSettings(settings);
		renderMicrophoneSettings(settings);

		const rate = Number(settings.speech_rate || 175);
		document.getElementById("speech-rate").value = rate;
		document.getElementById("speech-rate-value").textContent = String(rate);
	});
}

// Fetch commands and settings on page load
document.addEventListener("DOMContentLoaded", function () {
	bindSettingsEvents();
	fetchCommands();
	loadAppSettings();
});

// Add a command
function addCommand(type) {
    let name = document.getElementById(`${type}-name`).value.trim();
    let address = document.getElementById(`${type}-address`).value.trim();

    if (!name || !address) {
        alert("Please enter both name and address.");
        return;
    }

    eel.add_command(type, name, address)(function(response) {
        if (response.success) {
            fetchCommands();  // Refresh the list
        } else {
            alert(response.message);
        }
    });

    document.getElementById(`${type}-name`).value = "";
    document.getElementById(`${type}-address`).value = "";
}

// Fetch and display commands
function fetchCommands() {
    eel.get_commands()(function(commands) {
        updateList("web", commands.web);
        updateList("system", commands.system);
    });
}

// Update command lists
function updateList(type, commands) {
    let list = document.getElementById(`${type}-list`);
    list.innerHTML = "";

    commands.forEach(command => {
        let li = document.createElement("li");
		li.innerHTML = `<span>${command.name} - ${command.address}</span>
						<button class='delete-btn' onclick='deleteCommand("${type}", ${command.id})'>Delete</button>`;
        list.appendChild(li);
    });
}

// Delete a command
function deleteCommand(type, id) {
    eel.delete_command(type, id)(function(response) {
        if (response.success) {
            fetchCommands();  // Refresh the list
        } else {
            alert("Failed to delete command.");
        }
    });
}
