package com.example.counteripapp

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : AppCompatActivity() {

    private lateinit var counterText: TextView
    private val handler = Handler(Looper.getMainLooper())
    private var seconds = 0

    // Ticks once a second while the activity is started. Watching this
    // value in logcat/UI is the intended way to observe whether the
    // process is running or has been suspended by the OS.
    private val tickRunnable = object : Runnable {
        override fun run() {
            seconds += 1
            counterText.text = "Uptime: $seconds s"
            handler.postDelayed(this, 1000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        counterText = findViewById(R.id.counterText)
        val fetchIpButton = findViewById<Button>(R.id.fetchIpButton)

        fetchIpButton.setOnClickListener {
            loadIpScreen()
        }
    }

    override fun onStart() {
        super.onStart()
        handler.post(tickRunnable)
    }

    override fun onStop() {
        super.onStop()
        handler.removeCallbacks(tickRunnable)
    }

    /**
     * Key function to set a breakpoint on.
     *
     * Everything from the outbound HTTPS request through the Intent
     * launch to SecondActivity happens here: fetchPublicIp() does the
     * actual network call, and the Intent below is what transitions to
     * the second screen. Breaking at the top of this function lets you
     * step into the request before it's made and inspect the response
     * before the screen transition occurs.
     */
    private fun loadIpScreen() {
        CoroutineScope(Dispatchers.Main).launch {
            val ip = withContext(Dispatchers.IO) {
                fetchPublicIp()
            }

            val intent = Intent(this@MainActivity, SecondActivity::class.java)
            intent.putExtra(SecondActivity.EXTRA_IP, ip)
            startActivity(intent)
        }
    }

    private fun fetchPublicIp(): String {
        val url = URL("https://api.ipify.org")
        val connection = url.openConnection() as HttpURLConnection
        return try {
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000
            connection.connect()

            val responseCode = connection.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                    reader.readText()
                }
            } else {
                "Error: HTTP $responseCode"
            }
        } catch (e: Exception) {
            "Error: ${e.message}"
        } finally {
            connection.disconnect()
        }
    }
}
