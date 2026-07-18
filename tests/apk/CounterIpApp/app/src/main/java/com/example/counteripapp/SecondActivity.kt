package com.example.counteripapp

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SecondActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_IP = "extra_ip"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)

        val ipText = findViewById<TextView>(R.id.ipText)
        val exitButton = findViewById<Button>(R.id.exitButton)

        val ip = intent.getStringExtra(EXTRA_IP) ?: "Unknown"
        ipText.text = "Public IP: $ip"

        exitButton.setOnClickListener {
            // finishAffinity() closes every activity in this task.
            // Swap in System.exit(0) after it if you want the process
            // itself to die rather than just the UI stack finishing.
            finishAffinity()
        }
    }
}
